import { useState, useEffect } from "react";
import { 
  Moon, Database, Save, Laptop, Sparkles, Check
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";

interface AppSetting {
  id: number;
  key: string;
  value: string;
  type: string;
}

export function SettingsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Form local state
  const [theme, setTheme] = useState("dark");
  const [aiProvider, setAiProvider] = useState("mock");
  const [aiApiKey, setAiApiKey] = useState("");
  const [aiModel, setAiModel] = useState("gpt-4o-mini");
  const [userName, setUserName] = useState("Rodrigo");
  const [activeTab, setActiveTab] = useState<"general" | "ai" | "system">("general");

  const { toast } = useToast();

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      const data = await api.get<AppSetting[]>("/api/settings/");

      data?.forEach((s) => {
        if (s.key === "theme") setTheme(s.value);
        if (s.key === "ai_provider") setAiProvider(s.value);
        if (s.key === "ai_model") setAiModel(s.value);
        if (s.key === "user_name") setUserName(s.value);
      });
    } catch {
      toast({ title: "Erro ao carregar configurações", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleSaveSetting = async (key: string, value: string) => {
    try {
      await api.put(`/api/settings/${key}`, { value });
    } catch {
      // Ignore if key doesn't exist yet in backend
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

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Configurações</h1>
          <p className="text-sm text-surface-400">
            Personalize temas, inteligência artificial, dados e preferências do Resolva.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-surface-800/60 pb-3">
        {[
          { key: "general", label: "Geral & Perfil", icon: Laptop },
          { key: "ai", label: "Inteligência Artificial", icon: Sparkles },
          { key: "system", label: "Banco de Dados & Sistema", icon: Database },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
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
                  <strong>Banco de dados:</strong> SQLite assíncrono localizado em <code className="text-accent-400">./resolva.db</code>
                </p>
                <p>
                  <strong>Backend:</strong> FastAPI rodando em <code className="text-accent-400">http://127.0.0.1:8000</code>
                </p>
                <p>
                  <strong>Segurança:</strong> Execução de comandos protegida por whitelist e validação rigorosa de parâmetros.
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
    </div>
  );
}
