import { useState, useEffect, useMemo } from "react";
import { 
  Mail, Inbox, RefreshCw, Star, AlertCircle, 
  ShieldCheck, Archive, Trash2, CheckCircle2,
  Search, ExternalLink, Unlink, Sparkles, Send,
  
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";
import { formatDate } from "@/lib/utils";

interface EmailAccount {
  id: number;
  provider: string;
  email_address: string;
  is_active: boolean;
  last_synced_at: string | null;
  sync_status: string;
  sync_error: string | null;
}

interface Email {
  id: number;
  account_id: number;
  provider?: string;
  external_id: string;
  thread_id: string | null;
  from_address: string;
  from_name: string | null;
  to_addresses: string[];
  subject: string;
  body_preview: string | null;
  body_text: string | null;
  body_html: string | null;
  received_at: string;
  is_read: boolean;
  is_starred: boolean;
  is_important: boolean;
  labels: string[];
  ai_classification: string | null;
  ai_reasoning: string | null;
  needs_reply: boolean;
  synced_at: string | null;
}

interface EmailListResponse {
  items: Email[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface EmailSummary {
  unread_count: number;
  critical_count: number;
  important_count: number;
  needs_reply_count: number;
  total_count: number;
}

export function EmailsPage() {
  const [accounts, setAccounts] = useState<EmailAccount[]>([]);
  const [emails, setEmails] = useState<Email[]>([]);
  const [summary, setSummary] = useState<EmailSummary>({ 
    unread_count: 0, critical_count: 0, important_count: 0, needs_reply_count: 0, total_count: 0 
  });
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [providerFilter, setProviderFilter] = useState<"all" | "gmail" | "outlook">("all");
  const [filterType, setFilterType] = useState<"all" | "unread" | "critical" | "important" | "needs_reply">("all");
  const [searchQuery, setSearchQuery] = useState("");
  
  // Reply modal / state
  const [replyText, setReplyText] = useState("");
  const [isReplying, setIsReplying] = useState(false);
  const [showReplyBox, setShowReplyBox] = useState(false);

  const { toast } = useToast();

  const loadData = async () => {
    try {
      setIsLoading(true);
      const provParam = providerFilter !== "all" ? `&provider=${providerFilter}` : "";
      const [accs, listRes, sumRes] = await Promise.allSettled([
        api.get<EmailAccount[]>("/api/emails/accounts"),
        api.get<EmailListResponse>(`/api/emails/?page=1&page_size=100${provParam}`),
        api.get<EmailSummary>(`/api/emails/summary?provider=${providerFilter}`),
      ]);

      if (accs.status === "fulfilled") {
        setAccounts(accs.value || []);
      }
      if (listRes.status === "fulfilled") {
        const ems = listRes.value?.items || [];
        setEmails(ems);
        if (ems.length > 0) {
          if (!selectedEmail || !ems.some(e => e.id === selectedEmail.id)) {
            setSelectedEmail(ems[0]);
          }
        } else {
          setSelectedEmail(null);
        }
      }
      if (sumRes.status === "fulfilled") {
        setSummary(sumRes.value || { unread_count: 0, critical_count: 0, important_count: 0, needs_reply_count: 0, total_count: 0 });
      }
    } catch {
      toast({ title: "Erro ao carregar e-mails", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [providerFilter]);

  const handleConnectProvider = async (providerName: "gmail" | "outlook") => {
    try {
      const res = await api.post<{ authorization_url: string; state: string }>(`/api/emails/connect/${providerName}/init`);
      if (res?.authorization_url) {
        window.open(res.authorization_url, "_blank");
        toast({ title: `Navegador aberto para autenticação ${providerName === "gmail" ? "Google" : "Microsoft"}. Após autorizar, a conta será detectada automaticamente.`, type: "info" });

        // Poll para detectar quando a conta é conectada via callback
        const previousCount = accounts.length;
        let attempts = 0;
        const maxAttempts = 30;
        const pollInterval = setInterval(async () => {
          attempts++;
          try {
            const accs = await api.get<EmailAccount[]>("/api/emails/accounts");
            if (accs && accs.length > previousCount) {
              clearInterval(pollInterval);
              toast({ title: `Conta ${providerName.toUpperCase()} conectada com sucesso!`, type: "success" });
              await loadData();
            }
          } catch {
            //ignora erros de poll
          }
          if (attempts >= maxAttempts) {
            clearInterval(pollInterval);
          }
        }, 2000);
      }
    } catch {
      // Mock account fallback para testes locais
      try {
        await api.post(`/api/emails/connect/mock?provider=${providerName}`);
        toast({ title: `Conta ${providerName.toUpperCase()} de demonstração conectada!`, type: "success" });
        await loadData();
      } catch {
        toast({ title: `Erro ao conectar conta ${providerName}`, type: "error" });
      }
    }
  };

  const handleSyncEmails = async () => {
    setIsSyncing(true);
    try {
      const provParam = providerFilter !== "all" ? `?provider=${providerFilter}` : "";
      await api.post(`/api/emails/sync${provParam}`);
      toast({ title: "Caixa de entrada sincronizada com sucesso!", type: "success" });
      await loadData();
    } catch {
      toast({ title: "Não foi possível sincronizar. Os e-mails locais continuam disponíveis.", type: "warning" });
    } finally {
      setIsSyncing(false);
    }
  };

  const handleMarkRead = async (email: Email, isRead: boolean) => {
    try {
      await api.post(`/api/emails/${email.id}/read?is_read=${isRead}`);
      setEmails(emails.map(e => e.id === email.id ? { ...e, is_read: isRead } : e));
      if (selectedEmail?.id === email.id) {
        setSelectedEmail({ ...selectedEmail, is_read: isRead });
      }
      toast({ title: isRead ? "Marcado como lido" : "Marcado como não lido", type: "info" });
    } catch {
      toast({ title: "Erro ao atualizar status do email", type: "error" });
    }
  };

  const handleArchive = async (email: Email) => {
    try {
      await api.post(`/api/emails/${email.id}/archive`);
      setEmails(emails.filter(e => e.id !== email.id));
      if (selectedEmail?.id === email.id) {
        setSelectedEmail(emails.find(e => e.id !== email.id) || null);
      }
      toast({ title: "E-mail arquivado com sucesso!", type: "success" });
    } catch {
      toast({ title: "Erro ao arquivar e-mail", type: "error" });
    }
  };

  const handleTrash = async (email: Email) => {
    try {
      await api.post(`/api/emails/${email.id}/trash`);
      setEmails(emails.filter(e => e.id !== email.id));
      if (selectedEmail?.id === email.id) {
        setSelectedEmail(emails.find(e => e.id !== email.id) || null);
      }
      toast({ title: "E-mail movido para a lixeira", type: "success" });
    } catch {
      toast({ title: "Erro ao excluir e-mail", type: "error" });
    }
  };

  const handleDisconnect = async (accountId: number) => {
    if (!confirm("Deseja realmente desconectar esta conta de e-mail?")) return;
    try {
      await api.delete(`/api/emails/accounts/${accountId}`);
      toast({ title: "Conta desconectada com sucesso", type: "success" });
      await loadData();
    } catch {
      toast({ title: "Erro ao desconectar conta", type: "error" });
    }
  };

  const handleSendReply = async () => {
    if (!selectedEmail || !replyText.trim()) return;
    if (!confirm(`Confirmar envio de resposta para ${selectedEmail.from_address}?`)) return;

    setIsReplying(true);
    try {
      await api.post(`/api/emails/${selectedEmail.id}/reply`, {
        body: replyText,
        confirmed: true
      });
      toast({ title: "Resposta enviada com sucesso!", type: "success" });
      setReplyText("");
      setShowReplyBox(false);
    } catch {
      toast({ title: "Erro ao enviar resposta", type: "error" });
    } finally {
      setIsReplying(false);
    }
  };

  const filteredEmails = useMemo(() => {
    return emails.filter((e) => {
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchSubject = e.subject?.toLowerCase().includes(q);
        const matchFrom = (e.from_name || e.from_address).toLowerCase().includes(q);
        const matchSnippet = e.body_preview?.toLowerCase().includes(q);
        if (!matchSubject && !matchFrom && !matchSnippet) return false;
      }

      // Filter tabs
      if (filterType === "unread") return !e.is_read;
      if (filterType === "critical") return e.ai_classification === "CRITICAL" || e.ai_classification === "urgente";
      if (filterType === "important") return e.ai_classification === "IMPORTANT" || e.ai_classification === "importante" || e.ai_classification === "CRITICAL";
      if (filterType === "needs_reply") return e.needs_reply;
      return true;
    });
  }, [emails, filterType, searchQuery]);

  const getClassificationBadge = (cls: string | null) => {
    switch (cls?.toUpperCase()) {
      case "CRITICAL":
      case "URGENTE":
        return <Badge variant="error">Crítico</Badge>;
      case "IMPORTANT":
      case "IMPORTANTE":
        return <Badge variant="warning">Importante</Badge>;
      case "NEWSLETTER":
        return <Badge variant="outline" className="text-text-secondary border-border">Newsletter</Badge>;
      case "NORMAL":
        return <Badge variant="secondary">Normal</Badge>;
      default:
        return null;
    }
  };

  const getProviderTag = (provider?: string) => {
    const p = provider?.toLowerCase();
    if (p === "gmail") {
      return <span className="text-[10px] font-bold text-error bg-red-500/10 px-1.5 py-0.5 rounded border border-red-500/20">Gmail</span>;
    }
    if (p === "outlook" || p === "microsoft") {
      return <span className="text-[10px] font-bold text-info bg-blue-500/10 px-1.5 py-0.5 rounded border border-blue-500/20">Outlook</span>;
    }
    return <span className="text-[10px] font-bold text-text-secondary bg-surface-elevated px-1.5 py-0.5 rounded">Local</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header & Accounts Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Emails & Triagem IA</h1>
          <p className="text-sm text-text-secondary">
            Caixa de entrada unificada (Gmail + Outlook) com triagem inteligente e privacidade local.
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {accounts.map((acc) => (
            <div key={acc.id} className="flex items-center gap-2 bg-surface/80 border border-border px-3 py-1.5 rounded-lg text-xs">
              <span className={`w-2 h-2 rounded-full ${acc.provider === 'gmail' ? 'bg-red-400' : 'bg-blue-400'} animate-pulse`}></span>
              <span className="text-text-secondary font-medium">{acc.email_address}</span>
              <button 
                onClick={() => handleDisconnect(acc.id)} 
                title="Desconectar conta"
                className="text-text-muted hover:text-error ml-1 cursor-pointer transition-colors"
              >
                <Unlink className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}

          <div className="flex items-center gap-1.5">
            {!accounts.some(a => a.provider === "gmail") && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleConnectProvider("gmail")}
                className="gap-1.5 border-red-500/30 text-error hover:bg-red-500/10 text-xs"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                + Gmail
              </Button>
            )}
            {!accounts.some(a => a.provider === "outlook") && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleConnectProvider("outlook")}
                className="gap-1.5 border-blue-500/30 text-info hover:bg-blue-500/10 text-xs"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                + Outlook
              </Button>
            )}
          </div>

          <Button
            variant="outline"
            isLoading={isSyncing}
            onClick={handleSyncEmails}
            className="gap-2 border-border hover:text-text-primary"
          >
            <RefreshCw className="w-4 h-4" />
            Sincronizar
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-4 border-l-4 border-l-orange-500">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Não Lidos</span>
            <Inbox className="w-4 h-4 text-orange-400" />
          </div>
          <p className="text-2xl font-bold text-orange-400 tracking-tight">
            {summary.unread_count}
          </p>
        </div>

        <div className="glass-card p-4 border-l-4 border-l-red-500">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Críticos (Urgentes)</span>
            <AlertCircle className="w-4 h-4 text-error" />
          </div>
          <p className="text-2xl font-bold text-error tracking-tight">
            {summary.critical_count}
          </p>
        </div>

        <div className="glass-card p-4 border-l-4 border-l-yellow-500">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Prioritários</span>
            <Star className="w-4 h-4 text-warning" />
          </div>
          <p className="text-2xl font-bold text-warning tracking-tight">
            {summary.important_count}
          </p>
        </div>

        <div className="glass-card p-4 border-l-4 border-l-accent-500">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Aguardando Resposta</span>
            <Sparkles className="w-4 h-4 text-accent-light" />
          </div>
          <p className="text-2xl font-bold text-accent-light tracking-tight">
            {summary.needs_reply_count}
          </p>
        </div>
      </div>

      {/* Provider Selector and Filter Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Provider Scope Filter */}
          <div className="flex items-center bg-surface border border-border p-0.5 rounded-lg mr-2">
            {[
              { key: "all", label: "Todas as Caixas" },
              { key: "gmail", label: "Gmail" },
              { key: "outlook", label: "Outlook" },
            ].map((p) => (
              <button
                key={p.key}
                onClick={() => setProviderFilter(p.key as any)}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${
                  providerFilter === p.key
                    ? "bg-surface-hover text-text-primary font-semibold shadow-sm"
                    : "text-text-secondary hover:text-text-primary"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Classification Tabs */}
          {[
            { key: "all", label: "Todos" },
            { key: "unread", label: "Não Lidos" },
            { key: "critical", label: "Críticos" },
            { key: "important", label: "Prioritários (IA)" },
            { key: "needs_reply", label: "Aguardando Resposta" },
          ].map((f) => (
            <button
              key={f.key}
              onClick={() => setFilterType(f.key as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                filterType === f.key
                  ? "bg-accent/20 text-accent-light border border-accent/30"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-elevated/60"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-text-secondary absolute left-3 top-2.5" />
          <Input
            placeholder="Pesquisar (Gmail + Outlook)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 text-xs h-9 bg-surface/60"
          />
        </div>
      </div>

      {/* Main Mail Viewer Split View */}
      {isLoading ? (
        <LoadingState message="Carregando caixa de entrada unificada..." />
      ) : emails.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
          <div className="p-4 rounded-full bg-surface-elevated/50 mb-4 text-text-muted">
            <Mail className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-text-primary mb-1">
            Nenhum e-mail encontrado
          </h3>
          <p className="text-xs text-text-secondary max-w-sm mb-5">
            Conecte sua conta do Google Gmail ou Microsoft Outlook para gerenciar seus e-mails no Resolva.
          </p>
          <div className="flex items-center gap-3 flex-wrap justify-center">
            <Button onClick={() => handleConnectProvider("gmail")} size="sm" className="gap-1.5 bg-red-600 hover:bg-red-500">
              <ExternalLink className="w-4 h-4" />
              Conectar Gmail
            </Button>
            <Button onClick={() => handleConnectProvider("outlook")} size="sm" className="gap-1.5 bg-blue-600 hover:bg-blue-500">
              <ExternalLink className="w-4 h-4" />
              Conectar Outlook
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[560px]">
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
                      ? "border-accent bg-accent/10 shadow-sm"
                      : !email.is_read
                      ? "border-border/90 bg-surface-elevated/50 hover:bg-surface-elevated/80 font-medium"
                      : "border-border/80 bg-surface/60 hover:border-border hover:bg-surface-elevated/50 text-text-secondary"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 truncate">
                      {getProviderTag(email.provider)}
                      <span className={`text-xs truncate ${!email.is_read ? "font-bold text-text-primary" : "font-medium text-text-secondary"}`}>
                        {email.from_name || email.from_address}
                      </span>
                    </div>
                    <span className="text-[10px] text-text-muted whitespace-nowrap">
                      {formatDate(email.received_at)}
                    </span>
                  </div>

                  <h4 className={`text-xs truncate ${!email.is_read ? "font-semibold text-text-primary" : "text-text-secondary"}`}>
                    {email.subject}
                  </h4>

                  <p className="text-[11px] text-text-secondary line-clamp-1">
                    {email.body_preview || email.body_text}
                  </p>

                  <div className="flex items-center gap-1.5 pt-1 flex-wrap">
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
              <div className="space-y-5 overflow-y-auto pr-2 flex-1">
                {/* Email Header and Actions */}
                <div className="border-b border-border pb-4 space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        {getProviderTag(selectedEmail.provider)}
                        {getClassificationBadge(selectedEmail.ai_classification)}
                      </div>
                      <h2 className="text-lg font-bold text-text-primary tracking-tight leading-snug">
                        {selectedEmail.subject}
                      </h2>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleMarkRead(selectedEmail, !selectedEmail.is_read)}
                        title={selectedEmail.is_read ? "Marcar como não lido" : "Marcar como lido"}
                        className="text-text-secondary hover:text-text-primary p-1.5 h-8 w-8"
                      >
                        <CheckCircle2 className={`w-4 h-4 ${selectedEmail.is_read ? "text-success" : ""}`} />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleArchive(selectedEmail)}
                        title="Arquivar mensagem"
                        className="text-text-secondary hover:text-text-primary p-1.5 h-8 w-8"
                      >
                        <Archive className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleTrash(selectedEmail)}
                        title="Mover para lixeira"
                        className="text-text-secondary hover:text-error p-1.5 h-8 w-8"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between flex-wrap gap-2 text-xs text-text-secondary">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center font-bold text-text-primary text-xs">
                        {(selectedEmail.from_name || selectedEmail.from_address).charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <span className="font-semibold text-text-primary block">
                          {selectedEmail.from_name || selectedEmail.from_address}
                        </span>
                        <span className="text-text-muted text-[11px]">
                          &lt;{selectedEmail.from_address}&gt;
                        </span>
                      </div>
                    </div>
                    <span>{formatDate(selectedEmail.received_at)}</span>
                  </div>
                </div>

                {/* AI Insights Bar */}
                <div className="p-3 rounded-lg border border-accent/30 bg-accent/10 flex items-center justify-between gap-3 text-xs text-accent-300">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-accent-light shrink-0" />
                    <span>
                      <strong>Triagem Resolva IA:</strong> {selectedEmail.ai_reasoning || "Mensagem analisada e classificada localmente."}
                    </span>
                  </div>
                  {selectedEmail.needs_reply && (
                    <span className="text-[11px] font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/20 whitespace-nowrap">
                      Exige Resposta
                    </span>
                  )}
                </div>

                {/* Email Body with safe HTML or Plaintext */}
                <div className="text-sm text-text-primary leading-relaxed py-2">
                  {selectedEmail.body_html ? (
                    <div 
                      className="prose prose-invert max-w-none text-xs leading-relaxed overflow-x-auto"
                      dangerouslySetInnerHTML={{ __html: selectedEmail.body_html }}
                    />
                  ) : (
                    <div className="whitespace-pre-wrap">
                      {selectedEmail.body_text || selectedEmail.body_preview}
                    </div>
                  )}
                </div>

                {/* Action Bar / Reply Trigger */}
                <div className="pt-4 border-t border-border/80">
                  {!showReplyBox ? (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setShowReplyBox(true)}
                      className="gap-2 border-border text-text-secondary hover:text-text-primary"
                    >
                      <Send className="w-3.5 h-3.5" />
                      Responder com Confirmação
                    </Button>
                  ) : (
                    <div className="space-y-3 bg-surface/90 p-4 rounded-xl border border-border">
                      <div className="text-xs font-semibold text-text-secondary flex items-center justify-between">
                        <span>Nova Resposta para: <strong className="text-text-primary">{selectedEmail.from_address}</strong> ({selectedEmail.provider?.toUpperCase()})</span>
                        <Badge variant="outline" className="text-[10px] border-amber-500/40 text-warning">
                          Requer Confirmação Explícita
                        </Badge>
                      </div>
                      <textarea
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        placeholder="Digite sua resposta..."
                        rows={4}
                        className="w-full rounded-md border border-border bg-surface-elevated p-3 text-xs text-text-primary placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-accent-500"
                      />
                      <div className="flex items-center justify-end gap-2">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => { setShowReplyBox(false); setReplyText(""); }}
                        >
                          Cancelar
                        </Button>
                        <Button 
                          size="sm" 
                          isLoading={isReplying} 
                          onClick={handleSendReply}
                          className="gap-1.5"
                        >
                          <Send className="w-3.5 h-3.5" />
                          Confirmar & Enviar
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-text-muted">
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
