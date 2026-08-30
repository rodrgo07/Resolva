from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.email import Email, EmailAccount
from app.repositories.base import BaseRepository
from datetime import datetime

class EmailRepository(BaseRepository[Email]):
    def __init__(self, db: AsyncSession):
        super().__init__(Email, db)

    async def get_by_external_id(self, account_id: int, external_id: str) -> Optional[Email]:
        stmt = select(Email).where(
            and_(Email.account_id == account_id, Email.external_id == external_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_emails(
        self,
        account_id: Optional[int] = None,
        filter_type: Optional[str] = None,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Email], int]:
        stmt = select(Email)
        conditions = []

        if account_id:
            conditions.append(Email.account_id == account_id)

        if filter_type == "unread":
            conditions.append(Email.is_read == False)
        elif filter_type == "important":
            conditions.append(Email.ai_classification.in_(["CRITICAL", "IMPORTANT", "urgente", "importante"]))
        elif filter_type == "needs_reply":
            conditions.append(Email.needs_reply == True)
        elif filter_type == "starred":
            conditions.append(Email.is_starred == True)

        if search_query:
            q = f"%{search_query.lower()}%"
            conditions.append(
                or_(
                    func.lower(Email.subject).like(q),
                    func.lower(Email.from_address).like(q),
                    func.lower(Email.from_name).like(q),
                    func.lower(Email.body_preview).like(q)
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self.db.execute(count_stmt)
        total = total_res.scalar() or 0

        # Sort by received_at desc
        stmt = stmt.order_by(desc(Email.received_at)).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all()), total

    async def get_summary_stats(self, account_id: Optional[int] = None) -> Dict[str, int]:
        base_cond = [Email.account_id == account_id] if account_id else []

        unread_stmt = select(func.count(Email.id)).where(and_(*base_cond, Email.is_read == False))
        crit_stmt = select(func.count(Email.id)).where(and_(*base_cond, Email.ai_classification.in_(["CRITICAL", "urgente"])))
        imp_stmt = select(func.count(Email.id)).where(and_(*base_cond, Email.ai_classification.in_(["IMPORTANT", "importante"])))
        reply_stmt = select(func.count(Email.id)).where(and_(*base_cond, Email.needs_reply == True))
        total_stmt = select(func.count(Email.id)).where(and_(*base_cond)) if base_cond else select(func.count(Email.id))

        unread = (await self.db.execute(unread_stmt)).scalar() or 0
        critical = (await self.db.execute(crit_stmt)).scalar() or 0
        important = (await self.db.execute(imp_stmt)).scalar() or 0
        needs_reply = (await self.db.execute(reply_stmt)).scalar() or 0
        total = (await self.db.execute(total_stmt)).scalar() or 0

        return {
            "unread_count": unread,
            "critical_count": critical,
            "important_count": important,
            "needs_reply_count": needs_reply,
            "total_count": total
        }

    async def upsert_email(self, account_id: int, normalized_data: Dict[str, Any]) -> Tuple[Email, bool]:
        """
        Salva ou atualiza email de forma idempotente pelo external_id.
        Retorna (Email, created: bool).
        """
        existing = await self.get_by_external_id(account_id, normalized_data["external_id"])
        if existing:
            for k, v in normalized_data.items():
                if hasattr(existing, k) and k not in ["id", "account_id"]:
                    setattr(existing, k, v)
            existing.synced_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing)
            return existing, False
        else:
            normalized_data["account_id"] = account_id
            new_email = Email(**normalized_data)
            self.db.add(new_email)
            await self.db.commit()
            await self.db.refresh(new_email)
            return new_email, True
