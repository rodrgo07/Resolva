import { Settings, Palette, Bot, Zap, Globe, User } from "lucide-react";

const sections = [
  { id: "general", label: "Geral", icon: Settings },
  { id: "appearance", label: "Aparência", icon: Palette },
  { id: "ai", label: "IA", icon: Bot },
  { id: "automation", label: "Automação", icon: Zap },
  { id: "accounts", label: "Contas", icon: Globe },
  { id: "profile", label: "Perfil", icon: User },
];

export function SettingsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-surface-50">Configurações</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sections.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className="glass-card p-6 text-left hover:border-accent-500/20 transition-colors group"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded-lg bg-surface-800 text-surface-400 group-hover:text-accent-400 transition-colors">
                <Icon className="w-5 h-5" />
              </div>
              <h3 className="text-base font-medium text-surface-200">
                {label}
              </h3>
            </div>
            <p className="text-sm text-surface-500">
              {id === "general" && "Idioma, inicialização, notificações."}
              {id === "appearance" && "Tema, cor de destaque, densidade."}
              {id === "ai" && "Provedor, modelo, API key, memória."}
              {id === "automation" && "Permissões, comandos permitidos."}
              {id === "accounts" && "Gmail, Outlook, Google Calendar."}
              {id === "profile" && "Nome, avatar, preferências."}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
