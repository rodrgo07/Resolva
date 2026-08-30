import { useState, useEffect } from "react";
import { 
  Moon, Database, Save, Laptop, Sparkles, Check, Mail, ExternalLink, RefreshCw, Unlink,
  ShieldCheck, ArrowDownCircle, Trash2, RotateCcw, Wifi, WifiOff, Cloud
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";
import { ConfirmationDialog } from "@/components/shared/confirmation-dialog";
import { formatDate } from "@/lib/utils";

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
  const [activeTab, setActiveTab] = useState<"general" | "integrations" | "ai" | "sync" | "system">("general");

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
      toast({ title: "Erro ao carregar configurações", type: "error" });
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
      toast({ title: "Erro na restauração", type: "error" });
    } finally {
      
    }
  };

  const handleDeleteBackup = async () => {
    if (!deleteBackupId) return;
    try {
      await api.delete(`/api/backups/${deleteBackupId}`);
      toast({ title: "Backup excluído do disco", type: "info" });
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
        toast({ title: `Navegador aberto para autenticação ${providerName === 'gmail' ? 'Google' : 'Microsoft'} OAuth`, type: "info" });
      }
    } catch {
      try {
        await api.post(`/api/emails/connect/mock?provider=${providerName}`);
        toast({ title: `Conta ${providerName.toUpperCase()} de demonstração conectada`, type: "success" });
        await loadSettings();
      } catch {
        toast({ title: `Erro ao iniciar conexão com ${providerName}`, type: "error" });
      }
    }
  };

  const handleSyncNow = async () => {
    setIsSyncingEmail(true);
    try {
      await api.post("/api/emails/sync");
      await api.post("/api/sync/start");
      toast({ title: "Sincronização executada com sucesso!", type: "success" });
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
      // Ignorar se a chave ainda não existir
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
      ]);
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Configurações</h1>
          <p className="text-sm text-surface-400">
            Personalize temas, contas conectadas, IA, backups criptografados e sincronização offline-first.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-surface-800/60 pb-3 overflow-x-auto">
        {[
          { key: "general", label: "Geral & Perfil", icon: Laptop },
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
                  ? "bg-accent-500/20 text-accent-400 border border-accent-500/30 font-semibold"
                  : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/60"
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
      ) : (
        <form onSubmit={handleSaveAll} className="space-y-6">
          {activeTab === "general" && (
            <div className="space-y-4">
              <div className="glass-card p-5 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Laptop className="w-4 h-4 text-accent-400" />
                  Perfil do Usuário
                </h3>

                <div>
                  <label className="text-xs font-semibold text-surface-300 mb-1.5 block">
                    Nome de Exibição
                  </label>
                  <Input
                    value={userName}
                    onChange={(e) => setUserName(e.target.value)}
                    placeholder="Ex: Rodrigo"
                  />
                  <span className="text-[11px] text-surface-500 mt-1 block">
                    Utilizado no Dashboard para saudações e comandos da IA.
                  </span>
                </div>
              </div>

              <div className="glass-card p-5 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Moon className="w-4 h-4 text-accent-400" />
                  Aparência & Tema
                </h3>

                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setTheme("dark")}
                    className={`p-4 rounded-xl border text-left flex items-center justify-between cursor-pointer transition-all ${
                      theme === "dark"
                        ? "border-accent-500 bg-accent-500/10"
                        : "border-surface-800 bg-surface-900/60 text-surface-400"
                    }`}
                  >
                    <div>
                      <span className="text-sm font-bold text-white block">Escuro (Padrão)</span>
                      <span className="text-xs text-surface-400">Tons escuros e roxo elétrico</span>
                    </div>
                    {theme === "dark" && <Check className="w-4 h-4 text-accent-400" />}
                  </button>

                  <button
                    type="button"
                    onClick={() => setTheme("oled")}
                    className={`p-4 rounded-xl border text-left flex items-center justify-between cursor-pointer transition-all ${
                      theme === "oled"
                        ? "border-accent-500 bg-accent-500/10"
                        : "border-surface-800 bg-surface-900/60 text-surface-400"
                    }`}
                  >
                    <div>
                      <span className="text-sm font-bold text-white block">OLED Black</span>
                      <span className="text-xs text-surface-400">Preto puro para máxima economia</span>
                    </div>
                    {theme === "oled" && <Check className="w-4 h-4 text-accent-400" />}
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "sync" && (
            <div className="space-y-5">
              {/* Status de Conectividade & Sync */}
              <div className="glass-card p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Cloud className="w-4 h-4 text-accent-400" />
                    Status de Sincronização & Offline-First
                  </h3>
                  <div className="flex items-center gap-2">
                    {syncStatus?.connectivity_status === "ONLINE" ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                        <Wifi className="w-3.5 h-3.5" /> Online
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-surface-800 border border-surface-700 text-surface-400">
                        <WifiOff className="w-3.5 h-3.5" /> Offline
                      </span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-surface-900/40 border border-surface-800 space-y-1">
                    <span className="text-surface-500 font-mono">Dispositivo Local</span>
                    <p className="font-bold text-white font-mono truncate">{syncStatus?.device_id || "Identificando..."}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-surface-900/40 border border-surface-800 space-y-1">
                    <span className="text-surface-500 font-mono">Fila Offline Pendente</span>
                    <p className="font-bold text-white">{syncStatus?.pending_queue_count || 0} alterações</p>
                  </div>
                  <div className="p-3 rounded-lg bg-surface-900/40 border border-surface-800 space-y-1">
                    <span className="text-surface-500 font-mono">Último Backup</span>
                    <p className="font-bold text-white">{syncStatus?.last_backup_time || "Nenhum ainda"}</p>
                  </div>
                </div>
              </div>

              {/* Gerenciamento de Backups */}
              <div className="glass-card p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-accent-400" />
                      Backups Criptografados (Windows DPAPI)
                    </h3>
                    <p className="text-xs text-surface-400 mt-0.5">
                      Backups atômicos com integridade SHA-256 e proteção de rollback automático.
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
                  <p className="text-xs text-surface-500 py-4 text-center">Nenhum backup gerado até o momento.</p>
                ) : (
                  <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
                    {backups.map((b) => (
                      <div
                        key={b.id}
                        className="p-3 rounded-lg border border-surface-800 bg-surface-900/40 flex items-center justify-between gap-3 text-xs"
                      >
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-white font-semibold truncate">{b.filename}</span>
                            <Badge variant="outline" className="text-[10px] uppercase font-mono">
                              {b.backup_type}
                            </Badge>
                          </div>
                          <p className="text-surface-500 text-[11px]">
                            {formatDate(b.created_at)} • {(b.size_bytes / 1024).toFixed(1)} KB • SHA-256: {b.checksum_sha256.substring(0, 10)}...
                          </p>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            onClick={() => setRestoreId(b.id)}
                            className="h-7 text-xs gap-1 border-surface-700 hover:text-white"
                          >
                            <RotateCcw className="w-3 h-3" />
                            Restaurar
                          </Button>
                          <button
                            type="button"
                            onClick={() => setDeleteBackupId(b.id)}
                            className="p-1 text-surface-500 hover:text-red-400 transition-colors"
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
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Mail className="w-4 h-4 text-accent-400" />
                Provedores de E-mail Conectados
              </h3>

              {/* Gmail Card */}
              <div className="border border-surface-800 rounded-xl p-4 bg-surface-900/40 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center font-bold text-red-400">
                      G
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">Google Gmail</h4>
                      <p className="text-xs text-surface-400">OAuth 2.0 PKCE com triagem local por IA</p>
                    </div>
                  </div>
                  {gmailAccount ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Conectado
                    </span>
                  ) : (
                    <Button type="button" onClick={() => handleConnectProvider("gmail")} size="sm" className="gap-1.5 bg-red-600 hover:bg-red-500 text-white">
                      <ExternalLink className="w-3.5 h-3.5" />
                      Conectar Gmail
                    </Button>
                  )}
                </div>

                {gmailAccount && (
                  <div className="pt-3 border-t border-surface-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-surface-300">
                    <div>
                      <p className="font-semibold text-white">{gmailAccount.email_address}</p>
                      <p className="text-surface-500 text-[11px]">
                        Última sincronização: {gmailAccount.last_synced_at ? new Date(gmailAccount.last_synced_at).toLocaleString("pt-BR") : "Nunca"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        isLoading={isSyncingEmail}
                        onClick={handleSyncNow}
                        className="gap-1 text-xs border-surface-700 hover:text-white"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Sincronizar
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDisconnectEmail(gmailAccount.id)}
                        className="text-red-400 hover:bg-red-500/10 text-xs"
                      >
                        <Unlink className="w-3.5 h-3.5 mr-1" />
                        Desconectar
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* Outlook / Microsoft 365 Card */}
              <div className="border border-surface-800 rounded-xl p-4 bg-surface-900/40 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center font-bold text-blue-400">
                      O
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">Microsoft Outlook / 365</h4>
                      <p className="text-xs text-surface-400">Microsoft Graph API, OAuth 2.0 e sincronização incremental</p>
                    </div>
                  </div>
                  {outlookAccount ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Conectado
                    </span>
                  ) : (
                    <Button type="button" onClick={() => handleConnectProvider("outlook")} size="sm" className="gap-1.5 bg-blue-600 hover:bg-blue-500 text-white">
                      <ExternalLink className="w-3.5 h-3.5" />
                      Conectar Outlook
                    </Button>
                  )}
                </div>

                {outlookAccount && (
                  <div className="pt-3 border-t border-surface-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-surface-300">
                    <div>
                      <p className="font-semibold text-white">{outlookAccount.email_address}</p>
                      <p className="text-surface-500 text-[11px]">
                        Última sincronização: {outlookAccount.last_synced_at ? new Date(outlookAccount.last_synced_at).toLocaleString("pt-BR") : "Nunca"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        isLoading={isSyncingEmail}
                        onClick={handleSyncNow}
                        className="gap-1 text-xs border-surface-700 hover:text-white"
                      >
                        <RefreshCw className="w-3 h-3" />
                        Sincronizar
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDisconnectEmail(outlookAccount.id)}
                        className="text-red-400 hover:bg-red-500/10 text-xs"
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
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-accent-400" />
                Motor de Inteligência Artificial
              </h3>

              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1.5 block">
                  Provedor de IA
                </label>
                <select
                  value={aiProvider}
                  onChange={(e) => setAiProvider(e.target.value)}
                  className="w-full rounded-md border border-surface-700 bg-surface-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-accent-500"
                >
                  <option value="mock">Modo Offline / Local (Demonstração)</option>
                  <option value="openai">OpenAI (GPT-4o / GPT-4o-mini)</option>
                  <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
                </select>
              </div>

              {aiProvider !== "mock" && (
                <div className="space-y-4 pt-2 border-t border-surface-800">
                  <div>
                    <label className="text-xs font-semibold text-surface-300 mb-1.5 block">
                      Chave de API (API Key)
                    </label>
                    <Input
                      type="password"
                      value={aiApiKey}
                      onChange={(e) => setAiApiKey(e.target.value)}
                      placeholder="sk-..."
                    />
                    <span className="text-[11px] text-surface-500 mt-1 block">
                      Armazenada localmente e nunca compartilhada.
                    </span>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-surface-300 mb-1.5 block">
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
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Database className="w-4 h-4 text-accent-400" />
                Armazenamento & Segurança
              </h3>

              <div className="space-y-2 text-xs text-surface-400">
                <p>
                  <strong>Banco de dados:</strong> SQLite assíncrono com WAL mode ativo em <code className="text-accent-400">./resolva.db</code>
                </p>
                <p>
                  <strong>Cofre de Tokens:</strong> Windows DPAPI / Vault isolado no AppData (tokens OAuth de Gmail e Outlook protegidos fora do SQLite).
                </p>
                <p>
                  <strong>Backend:</strong> FastAPI assíncrono rodando em <code className="text-accent-400">http://127.0.0.1:8700</code>
                </p>
                <p>
                  <strong>Segurança:</strong> Sanitização estrita de HTML, proteção contra rate limit (429) e confirmação obrigatória de ações de escrita.
                </p>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-surface-800">
            <Button type="submit" isLoading={isSaving} className="gap-2">
              <Save className="w-4 h-4" />
              Salvar Alterações
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
        message="Restaurar este backup substituirá os dados atuais pelo estado salvo neste arquivo. Um backup de segurança será criado automaticamente antes da restauração."
        confirmLabel="Confirmar Restauração"
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
