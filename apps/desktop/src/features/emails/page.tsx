import { Mail } from "lucide-react";

export function EmailsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-surface-50">Emails</h1>
      </div>

      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="p-4 rounded-full bg-surface-800/50 mb-4">
          <Mail className="w-10 h-10 text-surface-600" />
        </div>
        <h3 className="text-lg font-medium text-surface-300 mb-2">
          Emails em breve
        </h3>
        <p className="text-sm text-surface-500 mb-6 max-w-sm">
          A integração com Gmail e Outlook será disponibilizada em breve.
          Por enquanto, a estrutura está preparada.
        </p>
      </div>
    </div>
  );
}
