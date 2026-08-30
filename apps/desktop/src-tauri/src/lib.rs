pub mod hotkeys;
pub mod tray;

use hotkeys::{HotkeyState, register_action_shortcut, unregister_all_hotkeys, register_default_hotkeys};
use tauri::{AppHandle, Manager, WindowEvent};
use std::sync::Mutex;
use std::process::{Child, Command, Stdio};
use std::path::{Path, PathBuf};
use std::fs::{File, OpenOptions};
use serde::{Deserialize, Serialize};

#[cfg(windows)]
use std::os::windows::process::CommandExt;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppWindowConfig {
    pub close_behavior: String,
    pub start_in_tray: bool,
    pub start_minimized: bool,
}

pub struct WindowConfigState {
    pub config: Mutex<AppWindowConfig>,
}

pub struct BackendProcessState {
    pub process: Mutex<Option<Child>>,
}

#[tauri::command]
fn update_hotkey(app: AppHandle, shortcut: String, action: String) -> Result<String, String> {
    register_action_shortcut(&app, &shortcut, &action)?;
    Ok(format!("Atalho '{}' registrado com sucesso para a ação '{}'", shortcut, action))
}

#[tauri::command]
fn set_close_behavior(app: AppHandle, behavior: String) -> Result<String, String> {
    let state = app.state::<WindowConfigState>();
    if let Ok(mut cfg) = state.config.lock() {
        cfg.close_behavior = behavior.clone();
    }
    Ok(format!("Comportamento ao fechar atualizado para: {}", behavior))
}

#[tauri::command]
fn show_main_window(app: AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.show();
        let _ = window.unminimize();
        let _ = window.set_focus();
        Ok(())
    } else {
        Err("Janela principal não encontrada".to_string())
    }
}

#[tauri::command]
fn hide_main_window(app: AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.hide();
        Ok(())
    } else {
        Err("Janela principal não encontrada".to_string())
    }
}

fn get_log_file_handle() -> Option<File> {
    let appdata = std::env::var("APPDATA").or_else(|_| std::env::var("LOCALAPPDATA")).ok()?;
    let log_dir = Path::new(&appdata).join("Resolva").join("logs");
    let _ = std::fs::create_dir_all(&log_dir);
    let log_file = log_dir.join("backend_stdout.log");
    OpenOptions::new().create(true).write(true).append(true).open(log_file).ok()
}

fn find_backend_and_python() -> Option<(PathBuf, PathBuf)> {
    let mut search_dirs = Vec::new();
    
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            search_dirs.push(parent.to_path_buf());
        }
    }
    if let Ok(cwd) = std::env::current_dir() {
        search_dirs.push(cwd);
    }
    search_dirs.push(PathBuf::from(r"C:\Users\thega\Documents\Resolva"));

    for base in search_dirs {
        for ancestor in base.ancestors() {
            // Caso 1: Monorepo dev (.venv/Scripts/python.exe + apps/backend)
            let venv_py = ancestor.join(".venv").join("Scripts").join("python.exe");
            let apps_backend = ancestor.join("apps").join("backend");
            if venv_py.exists() && apps_backend.exists() {
                return Some((venv_py, apps_backend));
            }

            // Caso 2: Pacote empacotado / instalado (python/python.exe + backend)
            let bundled_py = ancestor.join("python").join("python.exe");
            let bundled_backend = ancestor.join("backend");
            if bundled_py.exists() && bundled_backend.exists() {
                return Some((bundled_py, bundled_backend));
            }

            // Caso 3: .venv local com backend
            let local_venv_py = ancestor.join(".venv").join("Scripts").join("python.exe");
            if local_venv_py.exists() && bundled_backend.exists() {
                return Some((local_venv_py, bundled_backend));
            }
        }
    }

    None
}

fn spawn_backend_process() -> Option<Child> {
    #[cfg(windows)]
    const CREATE_NO_WINDOW: u32 = 0x08000000;

    if let Some((python_path, backend_dir)) = find_backend_and_python() {
        println!("[RESOLVA TAURI] Backend localizado. Python: {:?} | Dir: {:?}", python_path, backend_dir);
        
        let mut cmd = Command::new(&python_path);
        let run_server_script = backend_dir.join("run_server.py");
        if run_server_script.exists() {
            cmd.arg(&run_server_script);
        } else {
            cmd.args(["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8700"]);
        }

        cmd.current_dir(&backend_dir)
           .env("PYTHONUNBUFFERED", "1")
           .env("PYTHONPATH", &backend_dir);

        #[cfg(windows)]
        cmd.creation_flags(CREATE_NO_WINDOW);

        if let Some(log_file) = get_log_file_handle() {
            if let Ok(err_file) = log_file.try_clone() {
                cmd.stdout(Stdio::from(log_file));
                cmd.stderr(Stdio::from(err_file));
            }
        } else {
            cmd.stdout(Stdio::null());
            cmd.stderr(Stdio::null());
        }

        match cmd.spawn() {
            Ok(child) => {
                println!("[RESOLVA TAURI] Backend subprocess iniciado com sucesso. PID: {}", child.id());
                return Some(child);
            }
            Err(e) => {
                eprintln!("[RESOLVA TAURI ERROR] Falha ao iniciar subprocesso backend: {:?}", e);
            }
        }
    }


    // Fallback: tentar usar 'python' do PATH se não encontrado
    let mut fallback_cmd = Command::new("python");
    fallback_cmd.args(["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8700"])
                .env("PYTHONUNBUFFERED", "1");

    #[cfg(windows)]
    fallback_cmd.creation_flags(CREATE_NO_WINDOW);

    if let Some(log_file) = get_log_file_handle() {
        if let Ok(err_file) = log_file.try_clone() {
            fallback_cmd.stdout(Stdio::from(log_file));
            fallback_cmd.stderr(Stdio::from(err_file));
        }
    }

    if let Ok(child) = fallback_cmd.spawn() {
        println!("[RESOLVA TAURI] Backend iniciado via fallback 'python' global. PID: {}", child.id());
        return Some(child);
    }

    eprintln!("[RESOLVA TAURI ERROR] Não foi possível localizar o interpretador Python para iniciar o backend.");
    None
}


#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_autostart::init(tauri_plugin_autostart::MacosLauncher::LaunchAgent, Some(vec!["--autostart"])))
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
        }))
        .manage(HotkeyState::new())
        .manage(WindowConfigState {
            config: Mutex::new(AppWindowConfig {
                close_behavior: "minimize_to_tray".to_string(),
                start_in_tray: false,
                start_minimized: false,
            }),
        })
        .manage(BackendProcessState {
            process: Mutex::new(None),
        })
        .setup(|app| {
            let handle = app.handle().clone();

            // Iniciar processo do backend FastAPI
            let backend_child = spawn_backend_process();
            let backend_state = app.state::<BackendProcessState>();
            if let Ok(mut p) = backend_state.process.lock() {
                *p = backend_child;
            }

            // Configurar System Tray
            if let Err(e) = tray::setup_system_tray(&handle) {
                eprintln!("[WARN] Erro ao configurar system tray: {:?}", e);
            }

            // Registrar hotkeys padrão
            register_default_hotkeys(&handle);

            // Verificar flags de inicialização
            let args: Vec<String> = std::env::args().collect();
            let is_autostart = args.contains(&"--autostart".to_string()) || args.contains(&"--hidden".to_string());
            if is_autostart {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.hide();
                }
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                let app = window.app_handle();
                let state = app.state::<WindowConfigState>();
                let behavior = {
                    let cfg = state.config.lock().unwrap();
                    cfg.close_behavior.clone()
                };

                if behavior == "minimize_to_tray" {
                    api.prevent_close();
                    let _ = window.hide();
                } else {
                    // Finaliza hotkeys e mata o processo do backend
                    unregister_all_hotkeys(app);
                    let backend_state = app.state::<BackendProcessState>();
                    let proc = {
                        match backend_state.process.lock() {
                            Ok(mut lock) => lock.take(),
                            Err(_) => None,
                        }
                    };
                    if let Some(mut child) = proc {
                        let _ = child.kill();
                    }
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            update_hotkey,
            set_close_behavior,
            show_main_window,
            hide_main_window
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
