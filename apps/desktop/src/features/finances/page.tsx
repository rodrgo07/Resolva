import { useState, useEffect, useMemo } from "react";
import { 
  Plus, TrendingUp, TrendingDown, Wallet, 
  Trash2, Filter, Calendar, Tag, DollarSign,
  PieChart as PieChartIcon, ArrowUpRight, ArrowDownRight, Layers
} from "lucide-react";
import { 
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip as RechartsTooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from "recharts";
import { api } from "@/lib/api-client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { ConfirmationDialog } from "@/components/shared/confirmation-dialog";
import { LoadingState } from "@/components/shared/loading-state";
import { formatCurrency, formatDate } from "@/lib/utils";

type TransactionType = "expense" | "income";

interface Category {
  id: number;
  name: string;
  color: string;
  icon: string;
  type: string;
}

interface Transaction {
  id: number;
  amount: number;
  description: string;
  category_id: number | null;
  category: Category | null;
  date: string;
  type: TransactionType;
  recurrence: string | null;
  notes: string | null;
  created_at: string;
}

interface FinanceSummary {
  total_income: number;
  total_expense: number;
  balance: number;
}

interface CategoryBreakdown {
  category_name: string;
  total_amount: number;
  percentage: number;
}

interface Budget {
  id: number;
  category_id: number;
  limit_amount: number;
  period: string;
  year?: number;
  month?: number;
}

const CHART_COLORS = ["#8b5cf6", "#ec4899", "#3b82f6", "#f97316", "#10b981", "#eab308", "#6366f1"];

export function FinancesPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [summary, setSummary] = useState<FinanceSummary>({ total_income: 0, total_expense: 0, balance: 0 });
  const [breakdown, setBreakdown] = useState<CategoryBreakdown[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Filters & Tabs
  const [filterType, setFilterType] = useState<"all" | "expense" | "income">("all");
  const [activeTab, setActiveTab] = useState<"transactions" | "reports" | "budgets">("transactions");

  // Modal states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  // Form inputs
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [txType, setTxType] = useState<TransactionType>("expense");
  const [txDate, setTxDate] = useState(new Date().toISOString().split("T")[0]);
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { toast } = useToast();

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [txsData, catsData, sumData, breakData, budData] = await Promise.allSettled([
        api.get<Transaction[]>("/api/finances/transactions"),
        api.get<Category[]>("/api/finances/categories"),
        api.get<FinanceSummary>("/api/finances/summary"),
        api.get<CategoryBreakdown[]>("/api/finances/categories/breakdown"),
        api.get<Budget[]>("/api/finances/budgets"),
      ]);

      if (txsData.status === "fulfilled") setTransactions(txsData.value || []);
      if (catsData.status === "fulfilled") setCategories(catsData.value || []);
      if (sumData.status === "fulfilled") setSummary(sumData.value);
      if (breakData.status === "fulfilled") setBreakdown(breakData.value || []);
      if (budData.status === "fulfilled") setBudgets(budData.value || []);
    } catch {
      toast({ title: "Erro ao carregar dados financeiros", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenCreate = () => {
    setAmount("");
    setDescription("");
    setCategoryId(categories.length > 0 ? categories[0].id : "");
    setTxType("expense");
    setTxDate(new Date().toISOString().split("T")[0]);
    setNotes("");
    setIsFormOpen(true);
  };

  const handleSaveTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsedAmount = parseFloat(amount.replace(",", "."));
    if (isNaN(parsedAmount) || parsedAmount <= 0 || !description.trim()) {
      toast({ title: "Preencha o valor e a descrição corretamente", type: "warning" });
      return;
    }

    setIsSubmitting(true);
    const payload = {
      amount: parsedAmount,
      description: description.trim(),
      category_id: categoryId ? Number(categoryId) : null,
      type: txType,
      date: txDate,
      notes: notes.trim() || null,
    };

    try {
      await api.post("/api/finances/transactions", payload);
      toast({ title: "Lançamento registrado com sucesso", type: "success" });
      setIsFormOpen(false);
      loadData();
    } catch {
      toast({ title: "Erro ao registrar lançamento", type: "error" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await api.delete(`/api/finances/transactions/${deleteId}`);
      toast({ title: "Lançamento excluído com sucesso", type: "info" });
      setDeleteId(null);
      loadData();
    } catch {
      toast({ title: "Erro ao excluir lançamento", type: "error" });
    }
  };

  const filteredTransactions = useMemo(() => {
    return transactions.filter((t) => {
      if (filterType === "expense") return t.type === "expense";
      if (filterType === "income") return t.type === "income";
      return true;
    });
  }, [transactions, filterType]);

  const chartData = useMemo(() => {
    return breakdown.map((item, index) => ({
      name: item.category_name,
      value: item.total_amount,
      color: CHART_COLORS[index % CHART_COLORS.length],
    }));
  }, [breakdown]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Finanças</h1>
          <p className="text-sm text-text-secondary">
            Controle receitas, despesas, orçamentos e evolução financeira.
          </p>
        </div>
        <Button onClick={handleOpenCreate} className="gap-2 shrink-0">
          <Plus className="w-4 h-4" />
          Novo Lançamento
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 border-l-4 border-l-green-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Total Recebido</span>
            <div className="p-1.5 rounded-lg bg-green-500/10 text-success">
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-success tracking-tight">
            {formatCurrency(summary.total_income)}
          </p>
        </div>

        <div className="glass-card p-5 border-l-4 border-l-red-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Total Gasto</span>
            <div className="p-1.5 rounded-lg bg-red-500/10 text-error">
              <ArrowDownRight className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-error tracking-tight">
            {formatCurrency(summary.total_expense)}
          </p>
        </div>

        <div className="glass-card p-5 border-l-4 border-l-accent-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Saldo Líquido</span>
            <div className="p-1.5 rounded-lg bg-accent/10 text-accent-light">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <p className={`text-2xl font-bold tracking-tight ${summary.balance >= 0 ? "text-accent-light" : "text-error"}`}>
            {formatCurrency(summary.balance)}
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-border/60 pb-3">
        {[
          { key: "transactions", label: "Lançamentos", icon: Layers },
          { key: "reports", label: "Relatórios & Gráficos", icon: PieChartIcon },
          { key: "budgets", label: "Orçamentos", icon: DollarSign },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                activeTab === tab.key
                  ? "bg-accent/20 text-accent-light border border-accent/30"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-elevated/60"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <LoadingState message="Carregando informações financeiras..." />
      ) : activeTab === "transactions" ? (
        <div className="space-y-4">
          {/* Subfilters */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-text-muted ml-1" />
              {[
                { key: "all", label: "Todos" },
                { key: "expense", label: "Despesas" },
                { key: "income", label: "Receitas" },
              ].map((f) => (
                <button
                  key={f.key}
                  onClick={() => setFilterType(f.key as any)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${
                    filterType === f.key
                      ? "bg-surface-elevated text-text-primary border border-border"
                      : "text-text-secondary hover:text-text-primary"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
            <span className="text-xs text-text-muted">
              {filteredTransactions.length} registro(s) encontrado(s)
            </span>
          </div>

          {filteredTransactions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center glass-card border-dashed">
              <div className="p-4 rounded-full bg-surface-elevated/50 mb-3 text-text-muted">
                <Wallet className="w-8 h-8" />
              </div>
              <p className="text-sm font-semibold text-text-primary">Nenhum lançamento no período</p>
              <p className="text-xs text-text-secondary mt-1 mb-4">Adicione suas primeiras receitas ou despesas.</p>
              <Button onClick={handleOpenCreate} size="sm">Registrar Lançamento</Button>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredTransactions.map((tx) => {
                const isIncome = tx.type === "income";
                return (
                  <div
                    key={tx.id}
                    className="glass-card p-3.5 flex items-center justify-between gap-4 hover:border-border-strong transition-colors"
                  >
                    <div className="flex items-center gap-3.5 min-w-0">
                      <div className={`p-2 rounded-lg shrink-0 ${isIncome ? "bg-green-500/10 text-success" : "bg-red-500/10 text-error"}`}>
                        {isIncome ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-text-primary truncate">{tx.description}</span>
                          {tx.category && (
                            <Badge variant="outline" className="text-[10px] py-0 px-1.5 border-border">
                              {tx.category.name}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-[11px] text-text-secondary mt-0.5">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3 text-text-muted" />
                            {formatDate(tx.date)}
                          </span>
                          {tx.notes && <span className="truncate max-w-[200px] text-text-muted">Obs: {tx.notes}</span>}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 shrink-0">
                      <span className={`text-sm font-bold tracking-tight ${isIncome ? "text-success" : "text-error"}`}>
                        {isIncome ? "+ " : "- "}
                        {formatCurrency(tx.amount)}
                      </span>
                      <button
                        onClick={() => setDeleteId(tx.id)}
                        className="p-1 text-text-muted hover:text-error transition-colors cursor-pointer rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : activeTab === "reports" ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pie Chart: Categorias */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
              <PieChartIcon className="w-4 h-4 text-accent-light" />
              Gastos por Categoria
            </h3>
            {chartData.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-text-muted text-xs">
                Nenhum dado de despesas para exibir no gráfico.
              </div>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip 
                      formatter={(val: number) => [formatCurrency(val), "Gasto"]}
                      contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            {/* Category Legend */}
            <div className="mt-4 grid grid-cols-2 gap-2">
              {breakdown.map((item, i) => (
                <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-border/40">
                  <div className="flex items-center gap-2 truncate">
                    <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                    <span className="text-text-secondary truncate">{item.category_name}</span>
                  </div>
                  <span className="font-semibold text-text-primary ml-2">{formatCurrency(item.total_amount)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Bar Chart: Visão Geral */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-success" />
              Comparativo Receitas vs Despesas
            </h3>
            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    { name: "Receitas", valor: summary.total_income, fill: "#22c55e" },
                    { name: "Despesas", valor: summary.total_expense, fill: "#ef4444" },
                    { name: "Saldo", valor: Math.max(0, summary.balance), fill: "#8b5cf6" },
                  ]}
                  margin={{ top: 10, right: 10, left: 10, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={10} tickFormatter={(val) => `R$${val}`} />
                  <RechartsTooltip 
                    formatter={(val: number) => [formatCurrency(val), "Total"]}
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Bar dataKey="valor" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        /* Budgets Tab */
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-text-primary">Metas e Limites Orçamentários</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {budgets.map((b) => {
              const cat = categories.find(c => c.id === b.category_id);
              const spentForCat = transactions
                .filter(t => t.type === "expense" && t.category_id === b.category_id)
                .reduce((acc, t) => acc + t.amount, 0);
              const remaining = Math.max(0, b.limit_amount - spentForCat);
              const percentage = Math.min(100, Math.round((spentForCat / b.limit_amount) * 100));

              return (
                <div key={b.id} className="glass-card p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-lg bg-accent/10 text-accent-light">
                        <Tag className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-text-primary">{cat?.name || "Geral"}</h4>
                        <span className="text-[11px] text-text-secondary capitalize">{b.period}</span>
                      </div>
                    </div>
                    <Badge variant={percentage > 85 ? "error" : percentage > 60 ? "warning" : "success"}>
                      {percentage}% Usado
                    </Badge>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-surface-elevated rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        percentage > 85 ? "bg-red-500" : percentage > 60 ? "bg-yellow-500" : "bg-accent"
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-xs text-text-secondary pt-1">
                    <span>Gasto: <strong className="text-text-primary">{formatCurrency(spentForCat)}</strong></span>
                    <span>Limite: <strong className="text-text-primary">{formatCurrency(b.limit_amount)}</strong></span>
                    <span>Restante: <strong className="text-success">{formatCurrency(remaining)}</strong></span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Create Transaction Modal */}
      <Modal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        title="Novo Lançamento Financeiro"
        size="md"
      >
        <form onSubmit={handleSaveTransaction} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setTxType("expense")}
              className={`p-3 rounded-lg border text-sm font-medium flex items-center justify-center gap-2 transition-colors cursor-pointer ${
                txType === "expense"
                  ? "bg-red-500/10 border-red-500/40 text-error font-bold"
                  : "border-border bg-surface-elevated/40 text-text-secondary"
              }`}
            >
              <TrendingDown className="w-4 h-4" />
              Despesa
            </button>
            <button
              type="button"
              onClick={() => setTxType("income")}
              className={`p-3 rounded-lg border text-sm font-medium flex items-center justify-center gap-2 transition-colors cursor-pointer ${
                txType === "income"
                  ? "bg-green-500/10 border-green-500/40 text-success font-bold"
                  : "border-border bg-surface-elevated/40 text-text-secondary"
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              Receita
            </button>
          </div>

          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Valor (R$) *</label>
            <Input
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0,00"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Descrição *</label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ex: Almoço executivo, Supermercado"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Categoria</label>
              <select
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : "")}
                className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Data</label>
              <Input
                type="date"
                value={txDate}
                onChange={(e) => setTxDate(e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Observações (opcional)</label>
            <Input
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Ex: Pago via Pix, cartão de crédito..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-border">
            <Button variant="ghost" type="button" onClick={() => setIsFormOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Salvar Lançamento
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={deleteId !== null}
        onClose={() => setDeleteId(null)}
        onConfirm={handleDelete}
        title="Excluir Lançamento"
        message="Tem certeza que deseja excluir este registro financeiro? Os totais e gráficos serão recalculados."
        confirmLabel="Excluir"
        variant="destructive"
      />
    </div>
  );
}
