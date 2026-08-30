use tauri::{AppHandle, Manager, Emitter};
use tauri_plugin_global_shortcut::{GlobalShortcutExt, Shortcut, ShortcutState};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HotkeyConfig {
    pub command_palette: String,
    pub quick_task: String,
    pub agent: String,
    pub pomodoro: String,
}

impl Default for HotkeyConfig {
    fn default() -> Self {
        Self {
            command_palette: "Ctrl+Space".to_string(),
            quick_task: "Ctrl+Shift+T".to_string(),
            agent: "Ctrl+Shift+A".to_string(),
            pomodoro: "Ctrl+Shift+P".to_string(),
        }
    }
}

pub struct HotkeyState {
    pub registered: Mutex<HashMap<String, String>>,
}

impl HotkeyState {
    pub fn new() -> Self {
        Self {
            registered: Mutex::new(HashMap::new()),
        }
    }
}

pub fn normalize_shortcut(shortcut: &str) -> String {
    shortcut
        .replace(" ", "")
        .replace("Control", "Ctrl")
        .replace("CommandOrControl", "Ctrl")
}

pub fn register_default_hotkeys(app: &AppHandle) {
    let defaults = HotkeyConfig::default();
    let _ = register_action_shortcut(app, &defaults.command_palette, "open_command_palette");
    let _ = register_action_shortcut(app, &defaults.quick_task, "open_quick_task");
    let _ = register_action_shortcut(app, &defaults.agent, "open_agent");
    let _ = register_action_shortcut(app, &defaults.pomodoro, "open_pomodoro");
}

pub fn register_action_shortcut(app: &AppHandle, shortcut_str: &str, action: &str) -> Result<(), String> {
    let normalized = normalize_shortcut(shortcut_str);
    let shortcut: Shortcut = normalized.parse().map_err(|e| format!("Formato de atalho inválido: {:?}", e))?;
    
    {
        let state = app.state::<HotkeyState>();
        let mut map = state.registered.lock().unwrap();

        let prev_keys: Vec<String> = map.iter()
            .filter(|(_, act)| act.as_str() == action)
            .map(|(k, _)| k.clone())
            .collect();

        for prev in prev_keys {
            if let Ok(prev_sc) = prev.parse::<Shortcut>() {
                let _ = app.global_shortcut().unregister(prev_sc);
            }
            map.remove(&prev);
        }
    }

    let action_name = action.to_string();
    let app_handle = app.clone();

    app.global_shortcut().on_shortcut(shortcut, move |_app, _sc, event| {
        if event.state == ShortcutState::Pressed {
            if let Some(window) = app_handle.get_webview_window("main") {
                let _ = window.show();
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
            let _ = app_handle.emit("global-hotkey-triggered", &action_name);
        }
    }).map_err(|e| format!("Falha ao registrar atalho global '{}': {:?}", normalized, e))?;

    {
        let state = app.state::<HotkeyState>();
        let mut map = state.registered.lock().unwrap();
        map.insert(normalized, action.to_string());
    }
    Ok(())
}

pub fn unregister_all_hotkeys(app: &AppHandle) {
    let _ = app.global_shortcut().unregister_all();
    let state = app.state::<HotkeyState>();
    let mut map = state.registered.lock().unwrap();
    map.clear();
}
