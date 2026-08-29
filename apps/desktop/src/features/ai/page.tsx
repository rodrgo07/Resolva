import { useState, useEffect, useRef } from "react";
import { 
  Bot, Send, User, MessageSquare, 
  Trash2, Plus, ArrowRight, Loader2, Zap, CheckCircle2
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

const SUGGESTIONS = [
  "Quanto gastei essa semana?",
  "Quais tarefas estão atrasadas?",
  "O que tenho para fazer hoje?",
  "Quanto tempo estudei esta semana?",
  "Resuma meus compromissos de hoje",
  "Crie uma nova tarefa para estudar Rust",
];

export function AIPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvoId, setCurrentConvoId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);

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
        // Load latest conversation by default
        setCurrentConvoId(data[0].id);
        setMessages(data[0].messages || []);
      }
    } catch {
      toast({ title: "Erro ao carregar histórico de conversas", type: "error" });
    } finally {
      setIsHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
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
      toast({ title: "Erro ao carregar mensagens da conversa", type: "error" });
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
    } catch {
      toast({ title: "Erro ao se comunicar com a IA", type: "error" });
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

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] gap-4 animate-fade-in">
      {/* Sidebar: History */}
      <div className="w-full lg:w-72 glass-card p-4 flex flex-col justify-between shrink-0 h-48 lg:h-full">
        <div className="flex flex-col h-full min-h-0">
          <div className="flex items-center justify-between pb-3 mb-2 border-b border-surface-800">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-accent-400" />
              Histórico
            </h2>
            <Button
              size="sm"
              variant="outline"
              onClick={handleNewConversation}
              className="h-7 px-2 text-xs gap-1 border-surface-700 hover:text-white"
            >
              <Plus className="w-3.5 h-3.5" />
              Nova
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-1 pr-1 min-h-0">
            {isHistoryLoading ? (
              <div className="py-6 text-center text-xs text-surface-500">Carregando...</div>
            ) : conversations.length === 0 ? (
              <div className="py-6 text-center text-xs text-surface-500">
                Nenhuma conversa anterior
              </div>
            ) : (
              conversations.map((convo) => (
                <div
                  key={convo.id}
                  onClick={() => handleSelectConversation(convo.id)}
                  className={`flex items-center justify-between p-2 rounded-lg text-xs transition-all cursor-pointer group ${
                    currentConvoId === convo.id
                      ? "bg-accent-500/20 text-accent-400 font-semibold border border-accent-500/30"
                      : "text-surface-400 hover:text-white hover:bg-surface-800/60"
                  }`}
                >
                  <span className="truncate flex-1 pr-2">{convo.title}</span>
                  <button
                    onClick={(e) => handleDeleteConversation(e, convo.id)}
                    className="opacity-0 group-hover:opacity-100 hover:text-red-400 p-0.5 rounded transition-opacity"
                    title="Excluir conversa"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="pt-3 border-t border-surface-800/80 text-[11px] text-surface-500 flex items-center justify-between">
          <span>Provedor: Mock / Local</span>
          <span className="w-2 h-2 rounded-full bg-green-500" />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 glass-card flex flex-col justify-between overflow-hidden relative">
        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-xl mx-auto py-8">
              <div className="p-4 rounded-2xl bg-accent-500/10 text-accent-400 mb-4 border border-accent-500/20 shadow-lg shadow-accent-600/10">
                <Bot className="w-10 h-10" />
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight mb-2">
                Resolva AI — Seu Copiloto Pessoal
              </h2>
              <p className="text-xs text-surface-400 leading-relaxed mb-8 max-w-md">
                Posso consultar e organizar suas tarefas, analisar gastos, resumir métricas de estudo ou registrar novos afazeres para você.
              </p>

              {/* Suggestions Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
                {SUGGESTIONS.map((sug, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(sug)}
                    className="p-3 rounded-xl border border-surface-700/60 bg-surface-900/60 hover:bg-surface-800/80 hover:border-accent-500/40 text-left text-xs text-surface-300 hover:text-white transition-all flex items-center justify-between group cursor-pointer"
                  >
                    <span className="truncate pr-2">{sug}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-accent-400 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                  </button>
                ))}
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
                    <div className="w-8 h-8 rounded-xl bg-accent-600/20 border border-accent-500/30 flex items-center justify-center text-accent-400 shrink-0 mt-0.5">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      isUser
                        ? "bg-accent-600 text-white rounded-tr-sm shadow-md"
                        : "glass-card bg-surface-900/90 border border-surface-700/70 text-surface-100 rounded-tl-sm"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>

                    {/* AI Tool Calls badges */}
                    {!isUser && msg.tool_calls && msg.tool_calls.length > 0 && (
                      <div className="mt-2.5 pt-2 border-t border-surface-800/80 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] text-surface-400 flex items-center gap-1">
                          <Zap className="w-3 h-3 text-yellow-400" /> Ações executadas:
                        </span>
                        {msg.tool_calls.map((tool, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-surface-800 text-[10px] text-accent-400 border border-surface-700 font-mono"
                          >
                            <CheckCircle2 className="w-2.5 h-2.5 text-green-400" />
                            {tool}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-surface-800 border border-surface-700 flex items-center justify-center text-surface-300 shrink-0 mt-0.5">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {isLoading && (
            <div className="flex items-center gap-3 text-surface-400 text-xs py-2 animate-pulse">
              <div className="w-8 h-8 rounded-xl bg-accent-600/20 border border-accent-500/30 flex items-center justify-center text-accent-400">
                <Bot className="w-4 h-4" />
              </div>
              <div className="flex items-center gap-2 glass-card px-3 py-2 rounded-xl">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-accent-400" />
                <span>Resolva AI está pensando...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-surface-950/60 border-t border-surface-800/80">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center gap-2 glass p-1.5 rounded-xl border border-surface-700/80 focus-within:border-accent-500/80 transition-colors"
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Pergunte sobre tarefas, finanças ou peça para organizar seu dia..."
              disabled={isLoading}
              className="flex-1 bg-transparent px-3 py-1.5 text-sm text-white placeholder-surface-500 outline-none"
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
      </div>
    </div>
  );
}
