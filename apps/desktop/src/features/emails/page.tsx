import { useState, useEffect, useMemo } from "react";
import { 
  Mail, Inbox, RefreshCw, Star, AlertCircle, 
  ShieldCheck
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";
import { formatDate } from "@/lib/utils";

interface Email {
  id: number;
  account_id: number;
  from_address: string;
  from_name: string | null;
  subject: string;
  body_preview: string | null;
  received_at: string;
  is_read: boolean;
  ai_classification: string | null;
  needs_reply: boolean;
}

interface EmailSummary {
  unread_count: number;
  important_count: number;
  needs_reply_count: number;
}

export function EmailsPage() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [summary, setSummary] = useState<EmailSummary>({ unread_count: 0, important_count: 0, needs_reply_count: 0 });
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [filterType, setFilterType] = useState<"all" | "unread" | "important" | "needs_reply">("all");
  const { toast } = useToast();

  const loadEmailsData = async () => {
    try {
      setIsLoading(true);
      const [listData, sumData] = await Promise.allSettled([
        api.get<Email[]>("/api/emails/"),
        api.get<EmailSummary>("/api/emails/summary"),
      ]);

      if (listData.status === "fulfilled") {
        const ems = listData.value || [];
        setEmails(ems);
        if (ems.length > 0 && !selectedEmail) {
          setSelectedEmail(ems[0]);
        }
      }
      if (sumData.status === "fulfilled") setSummary(sumData.value);
    } catch {
      toast({ title: "Erro ao carregar emails", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEmailsData();
  }, []);

  const handleSyncEmails = async () => {
    setIsSyncing(true);
    try {
      await api.post("/api/emails/sync");
      toast({ title: "Caixa de entrada sincronizada!", type: "success" });
      await loadEmailsData();
    } catch {
      toast({ title: "Erro ao sincronizar emails", type: "error" });
    } finally {
      setIsSyncing(false);
    }
  };

  const filteredEmails = useMemo(() => {
    return emails.filter((e) => {
      if (filterType === "unread") return !e.is_read;
      if (filterType === "important") return e.ai_classification === "importante" || e.ai_classification === "urgente";
      if (filterType === "needs_reply") return e.needs_reply;
      return true;
    });
  }, [emails, filterType]);

  const getClassificationBadge = (cls: string | null) => {
    switch (cls) {
      case "urgente":
        return <Badge variant="error">Urgente</Badge>;
      case "importante":
        return <Badge variant="warning">Importante</Badge>;
      case "informativo":
        return <Badge variant="secondary">Informativo</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Emails & Triagem IA</h1>
          <p className="text-sm text-surface-400">
            Caixa de entrada inteligente com classificação de prioridade por IA.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            isLoading={isSyncing}
            onClick={handleSyncEmails}
            className="gap-2 border-surface-700 hover:text-white"
          >
            <RefreshCw className="w-4 h-4" />
            Sincronizar
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 border-l-4 border-l-orange-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-surface-400 uppercase tracking-wider">Não Lidos</span>
            <Inbox className="w-4 h-4 text-orange-400" />
          </div>
          <p className="text-2xl font-bold text-orange-400 tracking-tight">
            {summary.unread_count}
          </p>
        </div>

        <div className="glass-card p-5 border-l-4 border-l-yellow-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-surface-400 uppercase tracking-wider">Prioritários / Importantes</span>
            <Star className="w-4 h-4 text-yellow-400" />
          </div>
          <p className="text-2xl font-bold text-yellow-400 tracking-tight">
            {summary.important_count}
          </p>
        </div>

        <div className="glass-card p-5 border-l-4 border-l-red-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-surface-400 uppercase tracking-wider">Precisam de Resposta</span>
            <AlertCircle className="w-4 h-4 text-red-400" />
          </div>
          <p className="text-2xl font-bold text-red-400 tracking-tight">
            {summary.needs_reply_count}
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {[
          { key: "all", label: "Todos os Emails" },
          { key: "unread", label: "Não Lidos" },
          { key: "important", label: "Prioritários (IA)" },
          { key: "needs_reply", label: "Aguardando Resposta" },
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setFilterType(f.key as any)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              filterType === f.key
                ? "bg-accent-500/20 text-accent-400 border border-accent-500/30"
                : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/60"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Main Mail Viewer Split View */}
      {isLoading ? (
        <LoadingState message="Carregando caixa de entrada..." />
      ) : emails.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
          <div className="p-4 rounded-full bg-surface-800/50 mb-4 text-surface-500">
            <Mail className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-surface-200 mb-1">
            Caixa de entrada limpa
          </h3>
          <p className="text-xs text-surface-400 max-w-sm mb-5">
            Sincronize para buscar novas mensagens ou verificar notificações de emails.
          </p>
          <Button onClick={handleSyncEmails} isLoading={isSyncing} size="sm" className="gap-1.5">
            <RefreshCw className="w-4 h-4" />
            Sincronizar Agora
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
          {/* Email List Sidebar */}
          <div className="glass-card p-3 space-y-2 overflow-y-auto pr-1.5">
            {filteredEmails.map((email) => {
              const isSelected = selectedEmail?.id === email.id;
              return (
                <div
                  key={email.id}
                  onClick={() => setSelectedEmail(email)}
                  className={`p-3 rounded-lg border transition-all cursor-pointer space-y-1.5 ${
                    isSelected
                      ? "border-accent-500 bg-accent-500/10 shadow-sm"
                      : "border-surface-800/80 bg-surface-900/60 hover:border-surface-700 hover:bg-surface-800/50"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold text-white truncate">
                      {email.from_name || email.from_address}
                    </span>
                    <span className="text-[10px] text-surface-500 whitespace-nowrap">
                      {formatDate(email.received_at)}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-surface-200 truncate">
                    {email.subject}
                  </h4>

                  <p className="text-[11px] text-surface-400 line-clamp-1">
                    {email.body_preview}
                  </p>

                  <div className="flex items-center gap-2 pt-1">
                    {getClassificationBadge(email.ai_classification)}
                    {email.needs_reply && (
                      <Badge variant="outline" className="text-[9px] py-0 px-1 border-orange-500/30 text-orange-400">
                        Resposta Pendente
                      </Badge>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Email Reading Pane */}
          <div className="lg:col-span-2 glass-card p-6 flex flex-col justify-between overflow-hidden">
            {selectedEmail ? (
              <div className="space-y-6 overflow-y-auto pr-2">
                {/* Email Header */}
                <div className="border-b border-surface-800 pb-4 space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <h2 className="text-lg font-bold text-white tracking-tight leading-snug">
                      {selectedEmail.subject}
                    </h2>
                    <div className="flex items-center gap-2 shrink-0">
                      {getClassificationBadge(selectedEmail.ai_classification)}
                    </div>
                  </div>

                  <div className="flex items-center justify-between flex-wrap gap-2 text-xs text-surface-400">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-accent-600 flex items-center justify-center font-bold text-white text-xs">
                        {(selectedEmail.from_name || selectedEmail.from_address).charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <span className="font-semibold text-white block">
                          {selectedEmail.from_name || selectedEmail.from_address}
                        </span>
                        <span className="text-surface-500 text-[11px]">
                          &lt;{selectedEmail.from_address}&gt;
                        </span>
                      </div>
                    </div>
                    <span>{formatDate(selectedEmail.received_at)}</span>
                  </div>
                </div>

                {/* AI Insights Bar */}
                <div className="p-3 rounded-lg border border-accent-500/30 bg-accent-500/10 flex items-center justify-between gap-3 text-xs text-accent-300">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-accent-400 shrink-0" />
                    <span>
                      <strong>Classificação por IA:</strong> {selectedEmail.ai_classification === "importante" ? "Conteúdo de alta relevância profissional." : "Mensagem triada automaticamente."}
                    </span>
                  </div>
                  {selectedEmail.needs_reply && (
                    <span className="text-[11px] font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/20 whitespace-nowrap">
                      Exige Resposta
                    </span>
                  )}
                </div>

                {/* Email Body */}
                <div className="text-sm text-surface-200 leading-relaxed whitespace-pre-wrap py-2">
                  {selectedEmail.body_preview}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-surface-500">
                <Mail className="w-10 h-10 mb-2 opacity-30" />
                <p className="text-xs">Selecione um email para ler.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
