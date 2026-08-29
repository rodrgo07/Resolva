import { Activity, CheckSquare, Wallet, BookOpen, Zap, Bot } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";

const MOCK_ACTIVITIES = [
  {
    id: 1,
    type: "system",
    action: "Aplicativo iniciado",
    description: "Resolva foi iniciado com sucesso.",
    icon: Activity,
    color: "text-accent-400",
    created_at: new Date().toISOString(),
  },
];

const TYPE_ICONS: Record<string, { icon: React.ElementType; color: string }> = {
  task: { icon: CheckSquare, color: "text-accent-400" },
  finance: { icon: Wallet, color: "text-green-400" },
  study: { icon: BookOpen, color: "text-blue-400" },
  automation: { icon: Zap, color: "text-yellow-400" },
  ai: { icon: Bot, color: "text-purple-400" },
  system: { icon: Activity, color: "text-surface-400" },
};

export function ActivityPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold text-surface-50">Atividade</h1>

      <div className="space-y-1">
        {MOCK_ACTIVITIES.map((activity) => {
          const typeInfo = TYPE_ICONS[activity.type] || TYPE_ICONS.system;
          const Icon = typeInfo.icon;
          return (
            <div
              key={activity.id}
              className="flex items-center gap-4 p-3 rounded-lg hover:bg-surface-800/50 transition-colors"
            >
              <div className={`p-2 rounded-lg bg-surface-800 ${typeInfo.color}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-surface-200">
                  {activity.action}
                </p>
                <p className="text-xs text-surface-500 truncate">
                  {activity.description}
                </p>
              </div>
              <span className="text-xs text-surface-500 whitespace-nowrap">
                {formatRelativeTime(activity.created_at)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
