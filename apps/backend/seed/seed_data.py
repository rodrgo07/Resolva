import asyncio
from datetime import date, datetime, time, timedelta
from sqlalchemy import select
from app.database import async_session_maker
from app.models.task import Task, Subtask, TaskPriority, TaskStatus
from app.models.finance import Category, Expense, Budget, CategoryType, TransactionType, BudgetPeriod
from app.models.study import StudySubject, StudySession, SessionMode
from app.models.calendar import CalendarEvent
from app.models.notification import Notification
from app.models.activity import ActivityLog
from app.models.automation import Automation, AutomationTrigger, AutomationAction
from app.models.settings import AppSetting

async def seed_database():
    print("[SEED] Iniciando insercao dos dados de demonstracao no Resolva...")
    async with async_session_maker() as session:
        # Verificar se ja existem dados
        result = await session.execute(select(Task))
        if result.scalars().first():
            print("[INFO] O banco de dados ja contem registros. Seed ignorado.")
            return

        now = datetime.now()
        today = date.today()

        # 1. Categorias Financeiras e Gerais
        cat_alimentacao = Category(name="Alimentação", color="#f97316", icon="🍔", type=CategoryType.finance)
        cat_transporte = Category(name="Transporte", color="#3b82f6", icon="🚗", type=CategoryType.finance)
        cat_moradia = Category(name="Moradia", color="#8b5cf6", icon="🏠", type=CategoryType.finance)
        cat_lazer = Category(name="Lazer", color="#ec4899", icon="🎮", type=CategoryType.finance)
        cat_salario = Category(name="Salário", color="#22c55e", icon="💰", type=CategoryType.finance)
        
        session.add_all([cat_alimentacao, cat_transporte, cat_moradia, cat_lazer, cat_salario])
        await session.flush()

        # 2. Orçamentos
        budget_alimentacao = Budget(
            category_id=cat_alimentacao.id,
            limit_amount=600.00,
            period=BudgetPeriod.monthly,
            year=today.year,
            month=today.month
        )
        budget_transporte = Budget(
            category_id=cat_transporte.id,
            limit_amount=250.00,
            period=BudgetPeriod.monthly,
            year=today.year,
            month=today.month
        )
        session.add_all([budget_alimentacao, budget_transporte])

        # 3. Transações Financeiras (Receitas & Despesas)
        exp1 = Expense(
            amount=3500.00,
            description="Salário Mensal",
            category_id=cat_salario.id,
            date=today - timedelta(days=5),
            type=TransactionType.income,
            recurrence="monthly",
            notes="Depósito em conta corrente"
        )
        exp2 = Expense(
            amount=42.50,
            description="Almoço Executivo",
            category_id=cat_alimentacao.id,
            date=today,
            type=TransactionType.expense,
            recurrence="none",
            notes="Restaurante Central"
        )
        exp3 = Expense(
            amount=120.00,
            description="Supermercado Semanal",
            category_id=cat_alimentacao.id,
            date=today - timedelta(days=2),
            type=TransactionType.expense,
            recurrence="weekly"
        )
        exp4 = Expense(
            amount=50.00,
            description="Recarga Transporte",
            category_id=cat_transporte.id,
            date=today - timedelta(days=3),
            type=TransactionType.expense,
            recurrence="none"
        )
        exp5 = Expense(
            amount=89.90,
            description="Ingressos Cinema",
            category_id=cat_lazer.id,
            date=today - timedelta(days=1),
            type=TransactionType.expense,
            recurrence="none"
        )
        session.add_all([exp1, exp2, exp3, exp4, exp5])

        # 4. Tarefas e Subtarefas
        task1 = Task(
            title="Finalizar arquitetura do Resolva",
            description="Implementar models, rotas e banco SQLite de forma modular.",
            priority=TaskPriority.urgente,
            status=TaskStatus.em_andamento,
            category="Desenvolvimento",
            due_date=today,
            due_time=time(18, 0),
            recurrence="none",
            tags={"tags": ["dev", "resolva", "urgente"]}
        )
        task2 = Task(
            title="Estudar Rust & Tauri v2 IPC",
            description="Compreender o fluxo de sidecar e plugins nativos.",
            priority=TaskPriority.alta,
            status=TaskStatus.pendente,
            category="Estudos",
            due_date=today + timedelta(days=1),
            due_time=time(20, 0),
            tags={"tags": ["estudos", "rust"]}
        )
        task3 = Task(
            title="Pagar fatura de energia",
            description="Vencimento próximo da conta de luz.",
            priority=TaskPriority.media,
            status=TaskStatus.pendente,
            category="Finanças",
            due_date=today + timedelta(days=3),
            due_time=time(12, 0),
            tags={"tags": ["contas", "financas"]}
        )
        task4 = Task(
            title="Configurar ambiente Python 3.14",
            description="Instalar FastAPI, Alembic e SQLAlchemy.",
            priority=TaskPriority.alta,
            status=TaskStatus.concluida,
            completed_at=now - timedelta(hours=2),
            category="DevOps",
            due_date=today - timedelta(days=1),
            tags={"tags": ["setup", "python"]}
        )

        session.add_all([task1, task2, task3, task4])
        await session.flush()

        # Subtarefas
        sub1 = Subtask(task_id=task1.id, title="Criar modelos SQLAlchemy", completed=True, sort_order=1)
        sub2 = Subtask(task_id=task1.id, title="Rodar migração Alembic", completed=True, sort_order=2)
        sub3 = Subtask(task_id=task1.id, title="Integrar endpoints na UI", completed=False, sort_order=3)
        session.add_all([sub1, sub2, sub3])

        # 5. Matérias e Sessões de Estudo
        sub_rust = StudySubject(
            name="Rust & Tauri",
            description="Linguagem Rust e integração com Tauri v2",
            priority=3,
            progress=35.0,
            weekly_goal_hours=6.0,
            monthly_goal_hours=24.0,
            color="#f97316"
        )
        sub_fastapi = StudySubject(
            name="FastAPI & Async",
            description="Arquitetura limpa e alta performance com Python",
            priority=2,
            progress=70.0,
            weekly_goal_hours=4.0,
            monthly_goal_hours=16.0,
            color="#06b6d4"
        )
        sub_ai = StudySubject(
            name="IA & Agentes Autônomos",
            description="Function calling, permissões e orquestração de LLMs",
            priority=3,
            progress=50.0,
            weekly_goal_hours=5.0,
            monthly_goal_hours=20.0,
            color="#8b5cf6"
        )
        session.add_all([sub_rust, sub_fastapi, sub_ai])
        await session.flush()

        # Sessões de estudo
        sess1 = StudySession(
            subject_id=sub_rust.id,
            mode=SessionMode.pomodoro,
            started_at=now - timedelta(days=1, hours=2),
            ended_at=now - timedelta(days=1, hours=1),
            duration_minutes=60,
            notes="Leitura sobre gerenciamento de memória e ownership."
        )
        sess2 = StudySession(
            subject_id=sub_fastapi.id,
            mode=SessionMode.free,
            started_at=now - timedelta(hours=3),
            ended_at=now - timedelta(hours=2),
            duration_minutes=60,
            notes="Construção de repositórios assíncronos e routers."
        )
        session.add_all([sess1, sess2])

        # 6. Eventos do Calendário
        ev1 = CalendarEvent(
            title="Reunião de Alinhamento do Resolva",
            description="Apresentação do MVP e fluxo de IA",
            start_time=now + timedelta(days=1, hours=4),
            end_time=now + timedelta(days=1, hours=5),
            all_day=False,
            type="appointment",
            color="#8b5cf6",
            source="local"
        )
        ev2 = CalendarEvent(
            title="Sessão Focada: Estudos de IA",
            description="Implementação de novas AI Tools",
            start_time=now + timedelta(days=2, hours=2),
            end_time=now + timedelta(days=2, hours=4),
            all_day=False,
            type="study",
            color="#3b82f6",
            source="local"
        )
        session.add_all([ev1, ev2])

        # 7. Automação de Exemplo (Modo Programação)
        auto1 = Automation(
            name="Modo Programação",
            description="Prepara o ambiente de desenvolvimento completo.",
            is_active=True,
            icon="code"
        )
        session.add(auto1)
        await session.flush()

        trig1 = AutomationTrigger(
            automation_id=auto1.id,
            type="manual",
            config={"description": "Execução manual via painel ou atalho"}
        )
        act1 = AutomationAction(
            automation_id=auto1.id,
            type="open_application",
            config={"app_name": "code", "path": "C:\\Users\\thega\\Documents\\Resolva"},
            sort_order=1,
            requires_confirmation=False
        )
        act2 = AutomationAction(
            automation_id=auto1.id,
            type="send_notification",
            config={"title": "Modo Programação", "message": "Ambiente preparado com sucesso!"},
            sort_order=2,
            requires_confirmation=False
        )
        session.add_all([trig1, act1, act2])

        # 8. Notificações
        notif1 = Notification(
            type="task",
            title="Tarefa de Alta Prioridade",
            message="A tarefa 'Finalizar arquitetura do Resolva' vence hoje às 18:00.",
            priority="high",
            is_read=False
        )
        notif2 = Notification(
            type="finance",
            title="Alerta de Orçamento",
            message="Você atingiu 65% do seu orçamento mensal de Alimentação.",
            priority="normal",
            is_read=False
        )
        notif3 = Notification(
            type="system",
            title="Bem-vindo ao Resolva",
            message="Seu assistente pessoal digital está pronto para uso.",
            priority="low",
            is_read=True,
            read_at=now - timedelta(hours=5)
        )
        session.add_all([notif1, notif2, notif3])

        # 9. Logs de Atividade
        act_log1 = ActivityLog(
            type="system",
            action="Banco de dados inicializado",
            description="Tabelas e registros iniciais criados com sucesso.",
            metadata={"source": "seed"}
        )
        act_log2 = ActivityLog(
            type="task",
            action="Tarefa concluída",
            description="Configurar ambiente Python 3.14",
            metadata={"task_id": task4.id}
        )
        session.add_all([act_log1, act_log2])

        # 10. Configurações Globais
        settings_data = [
            AppSetting(key="app_language", value="pt-BR", type="string"),
            AppSetting(key="theme_mode", value="dark", type="string"),
            AppSetting(key="accent_color", value="#7c3aed", type="string"),
            AppSetting(key="ai_provider", value="mock", type="string"),
            AppSetting(key="user_name", value="Rodrigo", type="string"),
        ]
        session.add_all(settings_data)

        await session.commit()
        print("[SUCCESS] Dados de demonstracao inseridos com sucesso no SQLite!")

if __name__ == "__main__":
    asyncio.run(seed_database())
