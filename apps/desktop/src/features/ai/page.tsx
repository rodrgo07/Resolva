import { Bot, Send } from "lucide-react";
import { useState } from "react";

export function AIPage() {
  const [message, setMessage] = useState("");

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-surface-50">Resolva AI</h1>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col items-center justify-center text-center">
        <div className="p-6 rounded-full bg-accent-500/10 mb-6">
          <Bot className="w-12 h-12 text-accent-400" />
        </div>
        <h2 className="text-xl font-semibold text-surface-200 mb-2">
          Como posso ajudar?
        </h2>
        <p className="text-sm text-surface-400 max-w-md mb-8">
          Pergunte sobre suas tarefas, finanças, estudos ou peça para criar algo novo.
        </p>
        <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
          {[
            "Quanto gastei essa semana?",
            "Quais tarefas estão atrasadas?",
            "O que tenho para fazer hoje?",
            "Quanto estudei essa semana?",
          ].map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => setMessage(suggestion)}
              className="text-left text-sm p-3 rounded-lg border border-surface-700 hover:border-accent-500/30 hover:bg-surface-800/50 text-surface-400 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="mt-4">
        <div className="flex items-center gap-2 glass-card p-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Digite sua mensagem..."
            className="flex-1 bg-transparent text-surface-100 placeholder-surface-500 outline-none px-3 py-2 text-sm"
            onKeyDown={(e) => {
              if (e.key === "Enter" && message.trim()) {
                // TODO: send to AI
                setMessage("");
              }
            }}
          />
          <button
            disabled={!message.trim()}
            className="p-2 rounded-lg bg-accent-600 hover:bg-accent-700 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
