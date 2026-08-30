import { useState, useEffect } from "react";
import { 
  Moon, Database, Save, Laptop, Sparkles, Check, Mail, ExternalLink, RefreshCw, Unlink,
  ShieldCheck, ArrowDownCircle, Trash2, RotateCcw, Wifi, WifiOff, Cloud,
  Keyboard, Bell, Power, Smartphone
} from "lucide-react";
import { DeviceSettingsTab } from "./DeviceSettingsTab";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";
import { ConfirmationDialog } from "@/components/shared/confirmation-dialog";
import { formatDate } from "@/lib/utils";
import { useThemeStore, type ThemeMode } from "@/stores/theme-store";


interface AppSetting {
  id: number;
  key: string;
  value: string;
  type: string;
}

interface EmailAccount {
  id: number;
  provider: string;
  email_address: string;
  is_active: boolean;
  last_synced_at: string | null;
  sync_status: string;
  sync_error: string | null;
}

interface BackupItem {
  id: number;
  filename: string;
  size_bytes: number;
  checksum_sha256: string;
  is_encrypted: boolean;
  backup_type: string;
  status: string;
  schema_version: string;
  created_at: string;
}

interface SyncStatus {
  device_id: string;
  connectivity_status: "ONLINE" | "OFFLINE" | "CONNECTING" | "DEGRADED";
  pending_queue_count: number;
  conflicts_count: number;
  last_backup_time: string | null;
  last_sync_time: string | null;
}

export function SettingsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [emailAccounts, setEmailAccounts] = useState<EmailAccount[]>([]);
  const [isSyncingEmail, setIsSyncingEmail] = useState(false);

  // Backup & Sync States
  const [backups, setBackups] = useState<BackupItem[]>([]);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [isCreatingBackup, setIsCreatingBackup] = useState(false);
  const [restoreId, setRestoreId] = useState<number | null>(null);
  const [deleteBackupId, setDeleteBackupId] = useState<number | null>(null);
  

  // Form local state
  const [theme, setTheme] = useState("dark");
  const [aiProvider, setAiProvider] = useState("mock");
  const [aiApiKey, setAiApiKey] = useState("");
  const [aiModel, setAiModel] = useState("gpt-4o-mini");
  const [userName, setUserName] = useState("Rodrigo");

  // Fase 26: Windows Integration & Global Hotkeys
  const [startupEnabled, setStartupEnabled] = useState(false);
  const [startupMinimized, setStartupMinimized] = useState(false);
  const [startupTray, setStartupTray] = useState(false);
  const [closeBehavior, setCloseBehavior] = useState("minimize_to_tray");
  const [nativeNotifications, setNativeNotifications] = useState(true);

  // Global Hotkeys
  const [hkPalette, setHkPalette] = useState("Ctrl+Space");
  const [hkTask, setHkTask] = useState("Ctrl+Shift+T");
  const [hkAgent, setHkAgent] = useState("Ctrl+Shift+A");
  const [hkPomodoro, setHkPomodoro] = useState("Ctrl+Shift+P");

  // Notification categories
  const [notifTasks, setNotifTasks] = useState(true);
  const [notifCalendar, setNotifCalendar] = useState(true);
  const [notifEmails, setNotifEmails] = useState(true);
  const [notifStudies, setNotifStudies] = useState(true);
  const [notifFinances, setNotifFinances] = useState(true);
  const [notifAutomations, setNotifAutomations] = useState(true);

  const [activeTab, setActiveTab] = useState<"general" | "devices" | "windows" | "integrations" | "ai" | "sync" | "system">("general");

  const { toast } = useToast();

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      const [settingsData, accountsData, backupsData, syncData] = await Promise.allSettled([
        api.get<AppSetting[]>("/api/settings/"),
        api.get<EmailAccount[]>("/api/emails/accounts"),
        api.get<BackupItem[]>("/api/backups"),
        api.get<SyncStatus>("/api/sync/status")
      ]);

      if (settingsData.status === "fulfilled" && settingsData.value) {
        settingsData.value.forEach((s) => {
          if (s.key === "theme") setTheme(s.value);
          if (s.key === "ai_provider") setAiProvider(s.value);
          if (s.key === "ai_model") setAiModel(s.value);
          if (s.key === "user_name") setUserName(s.value);

          // Windows & Hotkeys settings
          if (s.key === "windows.startup_enabled") setStartupEnabled(s.value === "true");
          if (s.key === "windows.startup_minimized") setStartupMinimized(s.value === "true");
          if (s.key === "windows.startup_tray") setStartupTray(s.value === "true");
          if (s.key === "windows.close_behavior") setCloseBehavior(s.value);
          if (s.key === "windows.notifications_enabled") setNativeNotifications(s.value === "true");

          if (s.key === "hotkeys.command_palette") setHkPalette(s.value);
          if (s.key === "hotkeys.quick_task") setHkTask(s.value);
          if (s.key === "hotkeys.agent") setHkAgent(s.value);
          if (s.key === "hotkeys.pomodoro") setHkPomodoro(s.value);

          if (s.key === "notifications.tasks") setNotifTasks(s.value === "true");
          if (s.key === "notifications.calendar") setNotifCalendar(s.value === "true");
          if (s.key === "notifications.emails") setNotifEmails(s.value === "true");
          if (s.key === "notifications.studies") setNotifStudies(s.value === "true");
          if (s.key === "notifications.finances") setNotifFinances(s.value === "true");
          if (s.key === "notifications.automations") setNotifAutomations(s.value === "true");
        });
      }

      if (accountsData.status === "fulfilled" && accountsData.value) {
        setEmailAccounts(accountsData.value);
      }

      if (backupsData.status === "fulfilled" && backupsData.value) {
        setBackups(backupsData.value);
      }

      if (syncData.status === "fulfilled" && syncData.value) {
        setSyncStatus(syncData.value);
      }
    } catch {
      toast({ title: "Erro ao carregar configura��es", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleCreateBackup = async () => {
    setIsCreatingBackup(true);
    try {
      await api.post("/api/backups", { backup_type: "MANUAL" });
      toast({ title: "Backup criptografado criado com sucesso!", type: "success" });
      const bList = await api.get<BackupItem[]>("/api/backups");
      setBackups(bList || []);
    } catch {
      toast({ title: "Falha ao criar backup", type: "error" });
    } finally {
      setIsCreatingBackup(false);
    }
  };

  const handleConfirmRestore = async () => {
    if (!restoreId) return;
    
    try {
      await api.post(`/api/backups/${restoreId}/restore`, { confirmed: true });
      toast({ title: "Banco de dados restaurado com sucesso! Rollback preservado.", type: "success" });
      setRestoreId(null);
      loadSettings();
    } catch (err: any) {
      toast({ title: "Erro na restaura��o", type: "error" });
    } finally {
      
    }
  };

  const handleDeleteBackup = async () => {
    if (!deleteBackupId) return;
    try {
      await api.delete(`/api/backups/${deleteBackupId}`);
      toast({ title: "Backup exclu�do do disco", type: "info" });
      setDeleteBackupId(null);
      const bList = await api.get<BackupItem[]>("/api/backups");
      setBackups(bList || []);
    } catch {
      toast({ title: "Erro ao excluir backup", type: "error" });
    }
  };

  const handleConnectProvider = async (providerName: "gmail" | "outlook") => {
    try {
      const res = await api.post<{ authorization_url: string; state: string }>(`/api/emails/connect/${providerName}/init`);
      if (res?.authorization_url) {
        window.open(res.authorization_url, "_blank");
        toast({ title: `Navegador aberto para autentica��o ${providerName === 'gmail' ? 'Google' : 'Microsoft'} OAuth`, type: "info" });
      }
    } catch {
      try {
        await api.post(`/api/emails/connect/mock?provider=${providerName}`);
        toast({ title: `Conta ${providerName.toUpperCase()} de demonstra��o conectada`, type: "success" });
        await loadSettings();
      } catch {
        toast({ title: `Erro ao iniciar conex�o com ${providerName}`, type: "error" });
      }
    }
  };

  const handleSyncNow = async () => {
    setIsSyncingEmail(true);
    try {
      await api.post("/api/emails/sync");
      await api.post("/api/sync/start");
      toast({ title: "Sincroniza��o executada com sucesso!", type: "success" });
      await loadSettings();
    } catch {
      toast({ title: "Erro ao sincronizar", type: "error" });
    } finally {
      setIsSyncingEmail(false);
    }
  };

  const handleDisconnectEmail = async (id: number) => {
    if (!confirm("Deseja realmente desconectar esta conta?")) return;
    try {
      await api.delete(`/api/emails/accounts/${id}`);
      toast({ title: "Conta desconectada com sucesso", type: "success" });
      await loadSettings();
    } catch {
      toast({ title: "Erro ao desconectar conta", type: "error" });
    }
  };

  const handleSaveSetting = async (key: string, value: string) => {
    try {
      await api.put(`/api/settings/${key}`, { value });
    } catch {
      // Ignorar se a chave ainda n�o existir
    }
  };

  const handleSaveAll = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await Promise.allSettled([
        handleSaveSetting("theme", theme),
        handleSaveSetting("ai_provider", aiProvider),
        handleSaveSetting("ai_model", aiModel),
        handleSaveSetting("user_name", userName),
        // Windows & Hotkeys
        handleSaveSetting("windows.startup_enabled", startupEnabled.toString()),
        handleSaveSetting("windows.startup_minimized", startupMinimized.toString()),
        handleSaveSetting("windows.startup_tray", startupTray.toString()),
        handleSaveSetting("windows.close_behavior", closeBehavior),
        handleSaveSetting("windows.notifications_enabled", nativeNotifications.toString()),
        handleSaveSetting("hotkeys.command_palette", hkPalette),
        handleSaveSetting("hotkeys.quick_task", hkTask),
        handleSaveSetting("hotkeys.agent", hkAgent),
        handleSaveSetting("hotkeys.pomodoro", hkPomodoro),
        handleSaveSetting("notifications.tasks", notifTasks.toString()),
        handleSaveSetting("notifications.calendar", notifCalendar.toString()),
        handleSaveSetting("notifications.emails", notifEmails.toString()),
        handleSaveSetting("notifications.studies", notifStudies.toString()),
        handleSaveSetting("notifications.finances", notifFinances.toString()),
        handleSaveSetting("notifications.automations", notifAutomations.toString()),
      ]);

      // Sincronizar com Tauri se estiver no Desktop Host
      try {
        const { invoke } = await import("@tauri-apps/api/core");
        await invoke("set_close_behavior", { behavior: closeBehavior });
        await invoke("update_hotkey", { shortcut: hkPalette, action: "open_command_palette" });
        await invoke("update_hotkey", { shortcut: hkTask, action: "open_quick_task" });
        await invoke("update_hotkey", { shortcut: hkAgent, action: "open_agent" });
        await invoke("update_hotkey", { shortcut: hkPomodoro, action: "open_pomodoro" });

        // Autostart Plugin
        try {
          const { enable, disable } = await import("@tauri-apps/plugin-autostart");
          if (startupEnabled) {
            await enable();
          } else {
            await disable();
          }
        } catch {}
      } catch {}

      toast({ title: "Configurações salvas com sucesso!", type: "success" });
    } catch {
      toast({ title: "Erro ao salvar preferências", type: "error" });
    } finally {
      setIsSaving(false);
    }
  };

  const gmailAccount = emailAccounts.find(a => a.provider === "gmail");
  const outlookAccount = emailAccounts.find(a => a.provider === "outlook");

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Configura��es</h1>
          <p className="text-sm text-text-secondary">
            Personalize temas, contas conectadas, IA, backups criptografados e sincroniza��o offline-first.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-border/60 pb-3 overflow-x-auto">
        {[
          { key: "general", label: "Geral & Perfil", icon: Laptop },
          { key: "devices", label: "Dispositivos (Mobile)", icon: Smartphone },
          { key: "windows", label: "Windows & Atalhos", icon: Keyboard },
          { key: "integrations", label: "Integrações & E-mail", icon: Mail },
          { key: "sync", label: "Backup & Sincronização", icon: Cloud },
          { key: "ai", label: "Inteligência Artificial", icon: Sparkles },
          { key: "system", label: "Banco de Dados & Sistema", icon: Database },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
                activeTab === tab.key
                  ? "bg-accent/20 text-accent-light border border-accent/30 font-semibold"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-elevated/60"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <LoadingState message="Carregando preferências..." />
      ) : activeTab === "devices" ? (
        <DeviceSettingsTab />
      ) : (
        <form onSubmit={handleSaveAll} className="space-y-6">
          {activeTab === "general" && (
            <div className="space-y-4">
              <div className="glass-card p-5 space-y-4">
                <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                  <Laptop className="w-4 h-4 text-accent-light" />
                  Perfil do Usu�rio
                </h3>

                <div>
                  <label className="text-xs font-semibold text-text-secondary mb-1.5 block">
                    Nome de Exibi��o
                  </label>
                  <Input
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    placeholder="Ex: Rodrigo"
                  />
                  <span className="text-[11px] text-text-muted mt-1 block">
                    Utilizado no Dashboard para sauda��es e comandos da IA.
                    Utilizado no Dashboard para saudaes e comandos da IA.
                  </span>
                </div>
              </div>

              <div className="glass-card p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                    <Moon className="w-4 h-4 text-accent-light" />
                    Aparência & Sistema de Temas
                  </h3>
                  <Badge variant="outline" className="text-[10px] bg-accent/10 border-accent/30 text-accent-light">
                    5 Temas Ativos
                  </Badge>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {[
                    { id: "resolva" as ThemeMode, name: "RESOLVA (Padrão)", desc: "Azul cósmico profundo & Roxo", bgPreview: "bg-[#020617]", borderPreview: "border-[#7c3aed]" },
                    { id: "dark" as ThemeMode, name: "Dark Minimal", desc: "Tons de carvão & Índigo moderno", bgPreview: "bg-[#09090b]", borderPreview: "border-[#6366f1]" },
                    { id: "white" as ThemeMode, name: "White / Clean", desc: "Claro sofisticado & Alto contraste", bgPreview: "bg-[#f8fafc]", borderPreview: "border-[#4f46e5]" },
                    { id: "red" as ThemeMode, name: "Red / Crimson", desc: "Acentos carmesim & Foco enérgico", bgPreview: "bg-[#0c0a09]", borderPreview: "border-[#dc2626]" },
                    { id: "green" as ThemeMode, name: "Green / Emerald", desc: "Esmeralda produtiva & Bem-estar", bgPreview: "bg-[#022c22]", borderPreview: "border-[#16a34a]" },
                  ].map((t) => {
                    const isSelected = (useThemeStore.getState().theme || "resolva") === t.id;
                    return (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => {
                          useThemeStore.getState().setTheme(t.id);
                          setTheme(t.id);
                        }}
                        className={`p-3.5 rounded-xl border text-left flex flex-col justify-between gap-3 cursor-pointer transition-all ${
                          isSelected
                            ? "border-accent bg-accent/15 shadow-md shadow-accent-glow"
                            : "border-border bg-surface-elevated/40 hover:bg-surface-hover hover:border-accent/30"
                        }`}
                      >
                        <div className="flex items-center justify-between w-full">
                          <div className="flex items-center gap-2">
                            <div className={`w-3.5 h-3.5 rounded-full ${t.bgPreview} border-2 ${t.borderPreview} shadow-sm`} />
                            <span className="text-xs font-bold text-text-primary">{t.name}</span>
                          </div>
                          {isSelected && <Check className="w-3.5 h-3.5 text-accent-light" />}
                        </div>
                        <span className="text-[11px] text-text-secondary">{t.desc}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

            </div>
          )}

          {activeTab === "windows" && (
            <div className="space-y-6">
              {/* Global Hotkeys Card */}
              <div className="glass-card p-5 space-y-4">
                <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                  <Keyboard className="w-4 h-4 text-info" />
                  Atalhos Globais do Windows (Global Hotkeys)
                </h3>
                <p className="text-xs text-text-secondary">
                  Estes atalhos funcionam mesmo quando o Resolva estiver minimizado ou enquanto você estiver usando qualquer outro aplicativo do Windows.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div>
                    <label className="text-xs font-semibold text-text-secondary mb-1 block">
                      Command Palette Global
                    </label>
                    <Input 
                      value={hkPalette} 
                      onChange={(e) => setHkPalette(e.target.value)} 
                      placeholder="Ctrl+Space"
                    />
                    <span className="text-[11px] text-text-muted mt-0.5 block">Padrão: Ctrl+Space</span>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-text-secondary mb-1 block">
                      Criar Tarefa Rápida
                    </label>
                    <Input 
                      value={hkTask} 
                      onChange={(e) => setHkTask(e.target.value)} 
                      placeholder="Ctrl+Shift+T"
                    />
                    <span className="text-[11px] text-text-muted mt-0.5 block">Padrão: Ctrl+Shift+T</span>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-text-secondary mb-1 block">
                      Abrir Resolva Agent
                    </label>
                    <Input 
                      value={hkAgent} 
                      onChange={(e) => setHkAgent(e.target.value)} 
                      placeholder="Ctrl+Shift+A"
                    />
                    <span className="text-[11px] text-text-muted mt-0.5 block">Padrão: Ctrl+Shift+A</span>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-text-secondary mb-1 block">
                      Iniciar Pomodoro
                    </label>
                    <Input 
                      value={hkPomodoro} 
                      onChange={(e) => setHkPomodoro(e.target.value)} 
                      placeholder="Ctrl+Shift+P"
                    />
                    <span className="text-[11px] text-text-muted mt-0.5 block">Padrão: Ctrl+Shift+P</span>
                  </div>
                </div>
              </div>

              {/* System Tray & Close Behavior */}
              <div className="glass-card p-5 space-y-4">
                <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                  <Power className="w-4 h-4 text-success" />
                  Comportamento da Janela & System Tray
                </h3>

                <div className="space-y-3">
                  <div>
                    <label className="text-xs font-semibold text-text-secondary mb-1.5 block">
                      Ao fechar a janela principal (clique no X):
                    </label>
                    <select
                      value={closeBehavior}
                      onChange={(e) => setCloseBehavior(e.target.value)}
                      className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-500"
                    >
                      <option value="minimize_to_tray">Manter RESOLVA ativo na bandeja do Windows (Recomendado)</option>
                      <option value="exit_application">Encerrar o aplicativo completamente</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Windows Startup */}
              <div className="glass-card p-5 space-y-4">
                <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                  <Laptop className="w-4 h-4 text-accent-light" />
                  Inicialização com o Windows (Startup)
                </h3>

                <div className="space-y-3">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input 
                      type="checkbox"
                      checked={startupEnabled}
                      onChange={(e) => setStartupEnabled(e.target.checked)}
                      className="rounded border-border bg-surface text-accent focus:ring-accent-500"
                    />
                    <span className="text-sm text-text-primary">Iniciar RESOLVA automaticamente com o Windows</span>
                  </label>

                  <div className="pl-6 space-y-2">
                    <label className="flex items-center space-x-3 cursor-pointer opacity-90">
                      <input 
                        type="checkbox"
                        checked={startupMinimized}
                        onChange={(e) => setStartupMinimized(e.target.checked)}
                        disabled={!startupEnabled}
                        className="rounded border-border bg-surface text-accent focus:ring-accent-500 disabled:opacity-40"
                      />
                      <span className="text-xs text-text-secondary">Iniciar minimizado</span>
                    </label>

                    <label className="flex items-center space-x-3 cursor-pointer opacity-90">
                      <input 
                        type="checkbox"
                        checked={startupTray}
                        onChange={(e) => setStartupTray(e.target.checked)}
                        disabled={!startupEnabled}
                        className="rounded border-border bg-surface text-accent focus:ring-accent-500 disabled:opacity-40"
                      />
                      <span className="text-xs text-text-secondary">Iniciar direto na bandeja (sem abrir janela)</span>
                    </label>
                  </div>
                </div>
              </div>

              {/* Notifications Card */}
              <div className="glass-card p-5 space-y-4">
                <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                  <Bell className="w-4 h-4 text-warning" />
                  Notificações Nativas do Windows
                </h3>

                <label className="flex items-center space-x-3 cursor-pointer pb-2 border-b border-border">
                  <input 
                    type="checkbox"
                    checked={nativeNotifications}
                    onChange={(e) => setNativeNotifications(e.target.checked)}
                    className="rounded border-border bg-surface text-accent focus:ring-accent-500"
                  />
                  <span className="text-sm font-semibold text-text-primary">Habilitar notificações nativas do sistema</span>
                </label>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-1">
                  {[
                    { label: "Tarefas & Prazos", val: notifTasks, set: setNotifTasks },
                    { label: "Agenda & Compromissos", val: notifCalendar, set: setNotifCalendar },
                    { label: "E-mails Prioritários", val: notifEmails, set: setNotifEmails },
                    { label: "Estudos & Pomodoro", val: notifStudies, set: setNotifStudies },
                    { label: "Alertas de Finanças", val: notifFinances, set: setNotifFinances },
                    { label: "Rotinas & Automações", val: notifAutomations, set: setNotifAutomations },
                  ].map((cat, i) => (
                    <label key={i} className="flex items-center space-x-2 cursor-pointer">
                      <input 
                        type="checkbox"
                        checked={cat.val}
                        onChange={(e) => cat.set(e.target.checked)}
                        disabled={!nativeNotifications}
                        className="rounded border-border bg-surface text-accent focus:ring-accent-500 disabled:opacity-40"
                      />
                      <span className="text-xs text-text-secondary">{cat.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "sync" && (
            <div className="space-y-5">
              {/* Status de Conectividade & Sync */}
              <div className="glass-card p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                    <Cloud className="w-4 h-4 text-accent-light" />
                    Status de Sincroniza��o & Offline-First
                  </h3>
                  <div className="flex items-center gap-2">
                    {syncStatus?.connectivity_status === "ONLINE" ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-success">
                        <Wifi className="w-3.5 h-3.5" /> Online
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-surface-elevated border border-border text-text-secondary">
                        <WifiOff className="w-3.5 h-3.5" /> Offline
                      </span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-surface/40 border border-border space-y-1">
                    <span className="text-text-muted font-mono">Dispositivo Local</span>
                    <p className="font-bold text-text-primary font-mono truncate">{syncStatus?.device_id || "Identificando..."}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-surface/40 border border-border space-y-1">
                    <span className="text-text-muted font-mono">Fila Offline Pendente</span>
                    <p className="font-bold text-text-primary">{syncStatus?.pending_queue_count || 0} altera��es</p>
                  </div>
                  <div className="p-3 rounded-lg bg-surface/40 border border-border space-y-1">
                    <span className="text-text-muted font-mono">�ltimo Backup</span>
                    <p className="font-bold text-text-primary">{syncStatus?.last_backup_time || "Nenhum ainda"}</p>
                  </div>
                </div>
              </div>

              {/* Gerenciamento de Backups */}
              <div className="glass-card p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-accent-light" />
                      Backups Criptografados (Windows DPAPI)
                    </h3>
                    <p className="text-xs text-text-secondary mt-0.5">
                      Backups at�micos com integridade SHA-256 e prote��o de rollback autom�tico.
                    </p>
                  </div>

                  <Button
                    type="button"
                    size="sm"
                    isLoading={isCreatingBackup}
                    onClick={handleCreateBackup}
                    className="gap-1.5 text-xs"
                  >
                    <ArrowDownCircle className="w-3.5 h-3.5" />
                    Criar Backup Agora
                  </Button>
                </div>

                {backups.length === 0 ? (
                  <p className="text-xs text-text-muted py-4 text-center">Nenhum backup gerado at� o momento.</p>
                ) : (
                  <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
                    {backups.map((b) => (
                      <div
                        key={b.id}
                        className="p-3 rounded-lg border border-border bg-surface/40 flex items-center justify-between gap-3 text-xs"
                      >
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-text-primary font-semibold truncate">{b.filename}</span>
                            <Badge variant="outline" className="text-[10px] uppercase font-mono">
                              {b.backup_type}
                            </Badge>
                          </div>
                          <p className="text-text-muted text-[11px]">
                            {formatDate(b.created_at)} � {(b.size_bytes / 1024).toFixed(1)} KB � SHA-256: {b.checksum_sha256.substring(0, 10)}...
                          </p>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            onClick={() => setRestoreId(b.id)}
                            className="h-7 text-xs gap-1 border-border hover:text-text-primary"
                          >
                            <RotateCcw className="w-3 h-3" />
                            Restaurar
                          </Button>
                          <button
                            type="button"
                            onClick={() => setDeleteBackupId(b.id)}
                            className="p-1 text-text-muted hover:text-error transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "integrations" && (
            <div className="glass-card p-5 space-y-5">
              <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                <Mail className="w-4 h-4 text-accent-light" />
                Provedores de E-mail Conectados
              </h3>

              {/* Gmail Card */}
              <div className="border border-border rounded-xl p-4 bg-surface/40 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center font-bold text-error">
                      G
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-text-primary">Google Gmail</h4>
                      <p className="text-xs text-text-secondary">OAuth 2.0 PKCE com triagem local por IA</p>
                    </div>
                  </div>
                  {gmailAccount ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-success">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Conectado
                    </span>
                  ) : (
                    <Button type="button" onClick={() => handleConnectProvider("gmail")} size="sm" className="gap-1.5 bg-red-600 hover:bg-red-500 text-text-primary">
                      <ExternalLink className="w-3.5 h-3.5" />
                      Conectar Gmail
                    </Button>
                  )}
                </div>

                {gmailAccount && (
                  <div className="pt-3 border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-text-secondary">
                    <div>
                      <p className="font-semibold text-text-primary">{gmailAccount.email_address}</p>
                      <p className="text-text-muted text-[11px]">
                        �ltima sincroniza��o: {gmailAccount.last_synced_at ? new Date(gmailAccount.last_synced_at).toLocaleString("pt-BR") : "Nunca"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        isLoading={isSyncingEmail}
                        onClick={handleSyncNow}
                        className="gap-1 text-xs border-border hover:text-text-primary"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Sincronizar
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDisconnectEmail(gmailAccount.id)}
                        className="text-error hover:bg-red-500/10 text-xs"
                      >
                        <Unlink className="w-3.5 h-3.5 mr-1" />
                        Desconectar
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* Outlook / Microsoft 365 Card */}
              <div className="border border-border rounded-xl p-4 bg-surface/40 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center font-bold text-info">
                      O
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-text-primary">Microsoft Outlook / 365</h4>
                      <p className="text-xs text-text-secondary">Microsoft Graph API, OAuth 2.0 e sincroniza��o incremental</p>
                    </div>
                  </div>
                  {outlookAccount ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-success">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Conectado
                    </span>
                  ) : (
                    <Button type="button" onClick={() => handleConnectProvider("outlook")} size="sm" className="gap-1.5 bg-blue-600 hover:bg-blue-500 text-text-primary">
                      <ExternalLink className="w-3.5 h-3.5" />
                      Conectar Outlook
                    </Button>
                  )}
                </div>

                {outlookAccount && (
                  <div className="pt-3 border-t border-border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-text-secondary">
                    <div>
                      <p className="font-semibold text-text-primary">{outlookAccount.email_address}</p>
                      <p className="text-text-muted text-[11px]">
                        �ltima sincroniza��o: {outlookAccount.last_synced_at ? new Date(outlookAccount.last_synced_at).toLocaleString("pt-BR") : "Nunca"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        isLoading={isSyncingEmail}
                        onClick={handleSyncNow}
                        className="gap-1 text-xs border-border hover:text-text-primary"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Sincronizar
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDisconnectEmail(outlookAccount.id)}
                        className="text-error hover:bg-red-500/10 text-xs"
                      >
                        <Unlink className="w-3.5 h-3.5 mr-1" />
                        Desconectar
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "ai" && (
            <div className="glass-card p-5 space-y-4">
              <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-accent-light" />
                Motor de Intelig�ncia Artificial
              </h3>

              <div>
                <label className="text-xs font-semibold text-text-secondary mb-1.5 block">
                  Provedor de IA
                </label>
                <select
                  value={aiProvider}
                  onChange={(e) => setAiProvider(e.target.value)}
                  className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-500"
                >
                  <option value="mock">Modo Offline / Local (Demonstra��o)</option>
                  <option value="openai">OpenAI (GPT-4o / GPT-4o-mini)</option>
                  <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
                </select>
              </div>

              {aiProvider !== "mock" && (
                <div className="space-y-4 pt-2 border-t border-border">
                  <div>
                    <label className="text-xs font-semibold text-text-secondary mb-1.5 block">
                      Chave de API (API Key)
                    </label>
                    <Input
                      type="password"
                      value={aiApiKey}
                      onChange={(e) => setAiApiKey(e.target.value)}
                      placeholder="sk-..."
                    />
                    <span className="text-[11px] text-text-muted mt-1 block">
                      Armazenada localmente e nunca compartilhada.
                    </span>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-text-secondary mb-1.5 block">
                      Modelo
                    </label>
                    <Input
                      value={aiModel}
                      onChange={(e) => setAiModel(e.target.value)}
                      placeholder="gpt-4o-mini"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === "system" && (
            <div className="glass-card p-5 space-y-4">
              <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                <Database className="w-4 h-4 text-accent-light" />
                Armazenamento & Seguran�a
              </h3>

              <div className="space-y-2 text-xs text-text-secondary">
                <p>
                  <strong>Banco de dados:</strong> SQLite ass�ncrono com WAL mode ativo em <code className="text-accent-light">./resolva.db</code>
                </p>
                <p>
                  <strong>Cofre de Tokens:</strong> Windows DPAPI / Vault isolado no AppData (tokens OAuth de Gmail e Outlook protegidos fora do SQLite).
                </p>
                <p>
                  <strong>Backend:</strong> FastAPI ass�ncrono rodando em <code className="text-accent-light">http://127.0.0.1:8700</code>
                </p>
                <p>
                  <strong>Seguran�a:</strong> Sanitiza��o estrita de HTML, prote��o contra rate limit (429) e confirma��o obrigat�ria de a��es de escrita.
                </p>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-border">
            <Button type="submit" isLoading={isSaving} className="gap-2">
              <Save className="w-4 h-4" />
              Salvar Altera��es
            </Button>
          </div>
        </form>
      )}

      {/* Restore Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={restoreId !== null}
        onClose={() => setRestoreId(null)}
        onConfirm={handleConfirmRestore}
        title="Restaurar Banco de Dados"
        message="Restaurar este backup substituir� os dados atuais pelo estado salvo neste arquivo. Um backup de seguran�a ser� criado automaticamente antes da restaura��o."
        confirmLabel="Confirmar Restaura��o"
        variant="destructive"
      />

      {/* Delete Backup Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={deleteBackupId !== null}
        onClose={() => setDeleteBackupId(null)}
        onConfirm={handleDeleteBackup}
        title="Excluir Backup"
        message="Tem certeza que deseja excluir permanentemente este arquivo de backup do disco?"
        confirmLabel="Excluir do Disco"
        variant="destructive"
      />
    </div>
  );
}
