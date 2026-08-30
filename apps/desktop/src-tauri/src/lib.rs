pub mod hotkeys;
pub mod tray;

use hotkeys::{HotkeyState, register_action_shortcut, unregister_all_hotkeys, register_default_hotkeys};
use tauri::{AppHandle, Manager, WindowEvent};
use std::sync::Mutex;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppWindowConfig {
    pub close_behavior: String, // "minimize_to_tray" | "exit_application"
    pub start_in_tray: bool,
    pub start_minimized: bool,
}

pub struct WindowConfigState {
    pub config: Mutex<AppWindowConfig>,
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
        .setup(|app| {
            let handle = app.handle().clone();

            // Configurar System Tray
            if let Err(e) = tray::setup_system_tray(&handle) {
                eprintln!("[WARN] Erro ao configurar system tray: {:?}", e);
            }

            // Registrar hotkeys padrão (Ctrl+Space, Ctrl+Shift+T, Ctrl+Shift+A, Ctrl+Shift+P)
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
                    // Finaliza tudo de forma limpa
                    unregister_all_hotkeys(app);
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
