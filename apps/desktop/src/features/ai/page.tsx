import { useState, useEffect, useRef } from "react";
import { 
  Bot, Send, User, MessageSquare, 
  Trash2, Plus, ArrowRight, Loader2, Zap, CheckCircle2,
  Calendar, CheckSquare, Sparkles, AlertTriangle,
  Mail, ShieldCheck, History, X
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";

interface Message {
  id?: number;
  role: "user" | "assistant" | "system";
  content: string;
  tool_calls?: string[] | null;
  created_at?: string;
}

interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

interface ChatResponse {
  message: string;
  conversation_id: number;
  tool_calls_made: string[];
}

interface AgentActivity {
  id: number;
  action: string;
  description: string;
  timestamp: string;
  metadata_info?: any;
}

const QUICK_ACTIONS = [
  { label: "Organizar meu dia", prompt: "Resolva, organize meu dia com base nas minhas prioridades e agenda.", icon: Calendar },
  { label: "Ver pendências atrasadas", prompt: "Quais tarefas estão atrasadas e o que devo priorizar?", icon: AlertTriangle },
  { label: "E-mails prioritários", prompt: "Quais são os e-mails mais importantes que preciso responder hoje?", icon: Mail },
  { label: "Resumo financeiro", prompt: "Quanto gastei recentemente e como estão minhas finanças?", icon: Sparkles },
  { label: "O que fazer agora?", prompt: "Qual é a tarefa mais importante que devo focar exatamente agora?", icon: CheckSquare },
];

export function AIPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvoId, setCurrentConvoId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [showActivityDrawer, setShowActivityDrawer] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadConversations = async () => {
    try {
      setIsHistoryLoading(true);
      const data = await api.get<Conversation[]>("/api/ai/conversations");
      setConversations(data || []);
      if (data && data.length > 0 && currentConvoId === null) {
        setCurrentConvoId(data[0].id);
        setMessages(data[0].messages || []);
      }
    } catch {
      toast({ title: "Erro ao carregar histórico", type: "error" });
    } finally {
      setIsHistoryLoading(false);
    }
  };

  const loadActivities = async () => {
    try {
      const data = await api.get<AgentActivity[]>("/api/ai/activity");
      setActivities(data || []);
    } catch {
      // Ignore if empty
    }
  };

  useEffect(() => {
    loadConversations();
    loadActivities();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSelectConversation = async (convoId: number) => {
    setCurrentConvoId(convoId);
    try {
      const convo = await api.get<Conversation>(`/api/ai/conversations/${convoId}`);
      setMessages(convo.messages || []);
    } catch {
      toast({ title: "Erro ao carregar conversa", type: "error" });
    }
  };

  const handleNewConversation = () => {
    setCurrentConvoId(null);
    setMessages([]);
    setInputText("");
  };

  const handleDeleteConversation = async (e: React.MouseEvent, convoId: number) => {
    e.stopPropagation();
    try {
      await api.delete(`/api/ai/conversations/${convoId}`);
      toast({ title: "Conversa excluída", type: "info" });
      if (currentConvoId === convoId) {
        handleNewConversation();
      }
      loadConversations();
    } catch {
      toast({ title: "Erro ao excluir conversa", type: "error" });
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const message = textToSend || inputText;
    if (!message.trim() || isLoading) return;

    setInputText("");
    const userMsg: Message = { role: "user", content: message.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await api.post<ChatResponse>("/api/ai/chat", {
        message: message.trim(),
        conversation_id: currentConvoId || undefined,
      });

      const assistantMsg: Message = {
        role: "assistant",
        content: res.message,
        tool_calls: res.tool_calls_made,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      if (!currentConvoId) {
        setCurrentConvoId(res.conversation_id);
      }
      loadConversations();
      loadActivities();
    } catch {
      toast({ title: "Erro ao comunicar com o Resolva Agent", type: "error" });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Desculpe, ocorreu uma falha ao processar sua solicitação. Tente novamente.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearActivities = async () => {
    try {
      await api.delete("/api/ai/activity");
      setActivities([]);
      toast({ title: "Histórico de atividades limpo com sucesso!", type: "success" });
    } catch {
      toast({ title: "Erro ao limpar atividades", type: "error" });
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] gap-4 animate-fade-in">
      {/* Sidebar: History & Agent Capabilities */}
      <div className="w-full lg:w-72 glass-card p-4 flex flex-col justify-between shrink-0 h-52 lg:h-full">
        <div className="flex flex-col h-full min-h-0">
          <div className="flex items-center justify-between pb-3 mb-2 border-b border-border">
            <h2 className="text-sm font-bold text-text-primary flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-accent-light" />
              Sessões do Agent
            </h2>
            <div className="flex items-center gap-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowActivityDrawer(!showActivityDrawer)}
                title="Ver atividade e auditoria do Agent"
                className="h-7 w-7 p-0 text-text-secondary hover:text-text-primary"
              >
                <History className="w-3.5 h-3.5" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleNewConversation}
                className="h-7 px-2 text-xs gap-1 border-border hover:text-text-primary"
              >
                <Plus className="w-3.5 h-3.5" />
                Nova
              </Button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-1 pr-1 min-h-0">
            {isHistoryLoading ? (
              <div className="py-6 text-center text-xs text-text-muted">Carregando...</div>
            ) : conversations.length === 0 ? (
              <div className="py-6 text-center text-xs text-text-muted">
                Nenhuma sessão registrada
              </div>
            ) : (
              conversations.map((convo) => (
                <div
                  key={convo.id}
                  onClick={() => handleSelectConversation(convo.id)}
                  className={`flex items-center justify-between p-2 rounded-lg text-xs transition-all cursor-pointer group ${
                    currentConvoId === convo.id
                      ? "bg-accent/20 text-accent-light font-semibold border border-accent/30"
                      : "text-text-secondary hover:text-text-primary hover:bg-surface-elevated/60"
                  }`}
                >
                  <span className="truncate flex-1 pr-2">{convo.title}</span>
                  <button
                    onClick={(e) => handleDeleteConversation(e, convo.id)}
                    className="opacity-0 group-hover:opacity-100 hover:text-error p-0.5 rounded transition-opacity"
                    title="Excluir sessão"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="pt-3 border-t border-border/80 text-[11px] text-text-secondary flex items-center justify-between">
          <span className="flex items-center gap-1.5 font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-success" />
            Sandbox & Permissões Ativas
          </span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </div>

      {/* Main Agent Working Area */}
      <div className="flex-1 glass-card flex flex-col justify-between overflow-hidden relative">
        {/* Top Agent Bar */}
        <div className="px-5 py-3 border-b border-border/80 bg-background/40 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-accent/20 border border-accent/30 flex items-center justify-center text-accent-light">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-text-primary tracking-tight">RESOLVA AGENT</h3>
              <p className="text-[10px] text-text-secondary">Cérebro central de produtividade e orquestração</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleSendMessage("Resolva, organize meu dia.")}
              className="h-7 text-xs gap-1.5 border-accent/30 text-accent-light hover:bg-accent/10"
            >
              <Sparkles className="w-3 h-3" />
              Organizar Meu Dia
            </Button>
          </div>
        </div>

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-xl mx-auto py-8">
              <div className="p-4 rounded-2xl bg-accent/10 text-accent-light mb-4 border border-accent/20 shadow-lg shadow-accent-600/10">
                <Bot className="w-10 h-10" />
              </div>
              <h2 className="text-xl font-bold text-text-primary tracking-tight mb-2">
                RESOLVA AGENT — Produtividade Pessoal Orquestrada
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed mb-6 max-w-md">
                Compreendo seu contexto diário, organizo tarefas atrasadas, consulto compromissos, realizo triagem de e-mails (Gmail & Outlook) e sugiro blocos de tempo com total segurança local.
              </p>

              {/* Quick Actions Shortcuts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
                {QUICK_ACTIONS.map((qa, idx) => {
                  const Icon = qa.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(qa.prompt)}
                      className="p-3 rounded-xl border border-border/60 bg-surface/60 hover:bg-surface-elevated/80 hover:border-accent/40 text-left text-xs text-text-secondary hover:text-text-primary transition-all flex items-center justify-between group cursor-pointer"
                    >
                      <div className="flex items-center gap-2.5 truncate pr-2">
                        <Icon className="w-4 h-4 text-accent-light shrink-0" />
                        <span className="truncate">{qa.label}</span>
                      </div>
                      <ArrowRight className="w-3.5 h-3.5 text-accent-light opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            messages.map((msg, i) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={i}
                  className={`flex gap-3.5 ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-accent/20 border border-accent/30 flex items-center justify-center text-accent-light shrink-0 mt-0.5">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      isUser
                        ? "bg-accent text-text-primary rounded-tr-sm shadow-md"
                        : "glass-card bg-surface/90 border border-border/70 text-text-primary rounded-tl-sm"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>

                    {/* AI Tool Trace Badges */}
                    {!isUser && msg.tool_calls && msg.tool_calls.length > 0 && (
                      <div className="mt-2.5 pt-2 border-t border-border/80 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] text-text-secondary flex items-center gap-1">
                          <Zap className="w-3 h-3 text-warning" /> Ações orquestradas:
                        </span>
                        {msg.tool_calls.map((tool, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-surface-elevated text-[10px] text-accent-light border border-border font-mono"
                          >
                            <CheckCircle2 className="w-2.5 h-2.5 text-success" />
                            {tool}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-surface-elevated border border-border flex items-center justify-center text-text-secondary shrink-0 mt-0.5">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {isLoading && (
            <div className="flex items-center gap-3 text-text-secondary text-xs py-2 animate-pulse">
              <div className="w-8 h-8 rounded-xl bg-accent/20 border border-accent/30 flex items-center justify-center text-accent-light">
                <Bot className="w-4 h-4" />
              </div>
              <div className="flex items-center gap-2 glass-card px-3.5 py-2 rounded-xl border border-border">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-accent-light" />
                <span>RESOLVA AGENT está orquestrando seu contexto...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-background/60 border-t border-border/80">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-2 glass p-1.5 rounded-xl border border-border/80 focus-within:border-accent/80 transition-colors"
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Peça para organizar seu dia, consultar pendências ou triar emails..."
              disabled={isLoading}
              className="flex-1 bg-transparent px-3 py-1.5 text-sm text-text-primary placeholder-surface-500 outline-none"
            />
            <Button
              type="submit"
              size="sm"
              disabled={!inputText.trim() || isLoading}
              className="h-8 px-3 rounded-lg gap-1.5 font-semibold shrink-0"
            >
              <Send className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Enviar</span>
            </Button>
          </form>
        </div>

        {/* Agent Activity Drawer / Overlay */}
        {showActivityDrawer && (
          <div className="absolute inset-y-0 right-0 w-80 bg-surface/95 border-l border-border backdrop-blur-md p-4 shadow-2xl flex flex-col justify-between z-20 animate-fade-in">
            <div>
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-border">
                <div className="flex items-center gap-2 text-text-primary text-xs font-bold">
                  <History className="w-4 h-4 text-accent-light" />
                  Agent Activity & Auditoria
                </div>
                <button
                  onClick={() => setShowActivityDrawer(false)}
                  className="text-text-secondary hover:text-text-primary cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-2 overflow-y-auto max-h-[calc(100vh-16rem)] pr-1">
                {activities.length === 0 ? (
                  <p className="text-xs text-text-muted text-center py-6">
                    Nenhuma atividade registrada ainda.
                  </p>
                ) : (
                  activities.map((act) => (
                    <div key={act.id} className="p-2.5 rounded-lg bg-surface-elevated/40 border border-border text-xs space-y-1">
                      <div className="flex items-center justify-between text-[10px] text-text-secondary">
                        <span className="font-mono text-accent-light">{act.action}</span>
                        <span>{act.timestamp}</span>
                      </div>
                      <p className="text-text-secondary text-[11px]">{act.description}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="pt-3 border-t border-border">
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearActivities}
                className="w-full text-xs gap-1.5 border-border text-text-secondary hover:text-error hover:border-red-500/30"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Limpar Auditoria
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
