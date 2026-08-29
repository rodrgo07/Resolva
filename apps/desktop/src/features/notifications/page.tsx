import { Bell } from "lucide-react";

export function NotificationsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-surface-50">Notificações</h1>
        <button className="text-sm text-accent-400 hover:text-accent-300 transition-colors">
          Marcar todas como lidas
        </button>
      </div>

      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="p-4 rounded-full bg-surface-800/50 mb-4">
          <Bell className="w-10 h-10 text-surface-600" />
        </div>
        <h3 className="text-lg font-medium text-surface-300 mb-2">
          Nenhuma notificação
        </h3>
        <p className="text-sm text-surface-500 max-w-sm">
          Você será notificado sobre tarefas, estudos, finanças e automações aqui.
        </p>
      </div>
    </div>
  );
}
