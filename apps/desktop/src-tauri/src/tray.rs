use tauri::{
    menu::{Menu, MenuItem, PredefinedMenuItem},
    tray::{TrayIcon, TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState},
    AppHandle, Manager, Emitter,
};

pub fn setup_system_tray(app: &AppHandle) -> Result<TrayIcon, Box<dyn std::error::Error>> {
    let open_i = MenuItem::with_id(app, "tray_open", "Abrir RESOLVA", true, None::<&str>)?;
    let notifs_i = MenuItem::with_id(app, "tray_notifs", "Notificações", true, None::<&str>)?;
    let palette_i = MenuItem::with_id(app, "tray_palette", "Command Palette (Ctrl+Space)", true, None::<&str>)?;
    let task_i = MenuItem::with_id(app, "tray_task", "Nova Tarefa (Ctrl+Shift+T)", true, None::<&str>)?;
    let organize_i = MenuItem::with_id(app, "tray_organize", "Organizar meu dia", true, None::<&str>)?;
    let sep1 = PredefinedMenuItem::separator(app)?;

    let sync_i = MenuItem::with_id(app, "tray_sync", "Sincronização: Online", true, None::<&str>)?;
    let backup_i = MenuItem::with_id(app, "tray_backup", "Criar Backup Agora", true, None::<&str>)?;
    let sep2 = PredefinedMenuItem::separator(app)?;

    let pause_auto_i = MenuItem::with_id(app, "tray_pause_auto", "Pausar automações (Kill Switch)", true, None::<&str>)?;
    let resume_auto_i = MenuItem::with_id(app, "tray_resume_auto", "Retomar automações", true, None::<&str>)?;
    let sep3 = PredefinedMenuItem::separator(app)?;

    let settings_i = MenuItem::with_id(app, "tray_settings", "Configurações", true, None::<&str>)?;
    let quit_i = MenuItem::with_id(app, "tray_quit", "Sair do RESOLVA", true, None::<&str>)?;

    let menu = Menu::with_items(
        app,
        &[
            &open_i,
            &notifs_i,
            &palette_i,
            &task_i,
            &organize_i,
            &sep1,
            &sync_i,
            &backup_i,
            &sep2,
            &pause_auto_i,
            &resume_auto_i,
            &sep3,
            &settings_i,
            &quit_i,
        ],
    )?;

    let icon = app.default_window_icon().cloned().expect("Ícone padrão não encontrado");

    let tray = TrayIconBuilder::with_id("resolva-tray")
        .tooltip("RESOLVA — Assistente Pessoal Inteligente")
        .icon(icon)
        .menu(&menu)
        .show_menu_on_left_click(false)
        .on_menu_event(|app, event| {
            let id = event.id.as_ref();
            match id {
                "tray_open" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                }
                "tray_notifs" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                    let _ = app.emit("tray-action", "open_notifications");
                }
                "tray_palette" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                    let _ = app.emit("global-hotkey-triggered", "open_command_palette");
                }
                "tray_task" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                    let _ = app.emit("global-hotkey-triggered", "open_quick_task");
                }
                "tray_organize" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                    let _ = app.emit("tray-action", "organize_my_day");
                }
                "tray_sync" => {
                    let _ = app.emit("tray-action", "sync_now");
                }
                "tray_backup" => {
                    let _ = app.emit("tray-action", "create_backup");
                }
                "tray_pause_auto" => {
                    let _ = app.emit("tray-action", "pause_automations");
                }
                "tray_resume_auto" => {
                    let _ = app.emit("tray-action", "resume_automations");
                }
                "tray_settings" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                    let _ = app.emit("tray-action", "open_settings");
                }
                "tray_quit" => {
                    app.exit(0);
                }
                _ => {}
            }
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.show();
                        let _ = window.unminimize();
                        let _ = window.set_focus();
                    }
                }
            }
        })
        .build(app)?;

    Ok(tray)
}
