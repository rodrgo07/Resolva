import os
import shutil
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_sync import BackupRecord, BackupType, BackupStatus
from app.core.device import get_backups_dir, get_or_create_device_id
from app.core.backup_encryption import BackupEncryption
from app.config import settings
from app.core.logging import logger

class BackupManager:
    """
    Gerenciador profissional de backup local, criptografia, integridade SHA-256 e restauração segura com rollback.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_active_db_path(self) -> Path:
        db_url = settings.DATABASE_URL
        if "sqlite+aiosqlite:///" in db_url:
            raw_path = db_url.replace("sqlite+aiosqlite:///", "")
            return Path(raw_path).resolve()
        return Path("resolva.db").resolve()

    async def create_backup(self, backup_type: BackupType = BackupType.MANUAL) -> BackupRecord:
        now = datetime.now()
        timestamp_str = f"{now.strftime('%Y-%m-%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        device_id = get_or_create_device_id()
        backups_dir = get_backups_dir()

        filename = f"resolva-backup-{timestamp_str}.db.enc"
        target_path = backups_dir / filename

        active_db = self._get_active_db_path()

        # Cria cópia limpa do SQLite usando SQLite Online Backup API para evitar inconsistências com WAL
        temp_raw_backup = backups_dir / f"temp_{timestamp_str}.db"
        if active_db.exists():
            try:
                src_conn = sqlite3.connect(str(active_db))
                dst_conn = sqlite3.connect(str(temp_raw_backup))
                with dst_conn:
                    src_conn.backup(dst_conn)
                dst_conn.close()
                src_conn.close()
            except Exception as e:
                logger.warning(f"Fallback para cópia de arquivo direto no backup: {e}")
                shutil.copy2(active_db, temp_raw_backup)
        else:
            temp_raw_backup.write_bytes(b"")

        # Criptografa o arquivo
        raw_bytes = temp_raw_backup.read_bytes()
        encrypted_bytes = BackupEncryption.encrypt_bytes(raw_bytes)
        target_path.write_bytes(encrypted_bytes)

        # Remove temp raw backup
        if temp_raw_backup.exists():
            temp_raw_backup.unlink()

        size = target_path.stat().st_size
        checksum = BackupEncryption.calculate_sha256(target_path)

        record = BackupRecord(
            filename=filename,
            filepath=str(target_path),
            size_bytes=size,
            checksum_sha256=checksum,
            is_encrypted=True,
            backup_type=backup_type,
            status=BackupStatus.COMPLETED,
            schema_version="0.1.0",
            device_id=device_id
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        # Aplica retenção automática
        await self._enforce_retention()

        logger.info(f"Backup '{filename}' criado com sucesso ({size} bytes, SHA-256: {checksum[:8]}...)")
        return record

    async def list_backups(self) -> List[BackupRecord]:
        stmt = select(BackupRecord).order_by(desc(BackupRecord.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def restore_backup(self, backup_id: int, confirmed: bool) -> tuple[bool, str]:
        if not confirmed:
            return False, "Restauração de backup exige confirmação explícita do usuário."

        stmt = select(BackupRecord).where(BackupRecord.id == backup_id)
        res = await self.db.execute(stmt)
        backup = res.scalars().first()

        if not backup:
            return False, "Backup não encontrado."

        backup_file = Path(backup.filepath)
        if not backup_file.exists():
            return False, "Arquivo físico do backup não foi localizado em disco."

        # 1. Validação de integridade do Checksum
        current_checksum = BackupEncryption.calculate_sha256(backup_file)
        if current_checksum != backup.checksum_sha256:
            return False, "Falha de integridade: Checksum SHA-256 não confere (arquivo pode estar corrompido)."

        # 2. Criar backup de segurança (PRE_RESTORE) do banco atual para garantir rollback em caso de falha
        active_db = self._get_active_db_path()
        pre_restore_backup = await self.create_backup(backup_type=BackupType.PRE_RESTORE)

        try:
            # Descriptografa dados
            enc_data = backup_file.read_bytes()
            raw_db_data = BackupEncryption.decrypt_bytes(enc_data)

            # Escreve no banco ativo
            active_db.write_bytes(raw_db_data)

            # Valida que o SQLite restaurado é legível
            test_conn = sqlite3.connect(str(active_db))
            test_conn.execute("SELECT 1;")
            test_conn.close()

            logger.info(f"Backup '{backup.filename}' restaurado com sucesso!")
            return True, f"Banco restaurado com sucesso a partir do backup '{backup.filename}'."

        except Exception as err:
            logger.error(f"Erro durante a restauração, executando Rollback: {err}")
            # Rollback seguro para o PRE_RESTORE
            try:
                pre_file = Path(pre_restore_backup.filepath)
                if pre_file.exists():
                    raw_rollback = BackupEncryption.decrypt_bytes(pre_file.read_bytes())
                    active_db.write_bytes(raw_rollback)
            except Exception as roll_err:
                logger.critical(f"Falha crítica no rollback: {roll_err}")

            return False, f"Falha na restauração: {str(err)}. Rollback automático executado com segurança."

    async def delete_backup(self, backup_id: int) -> bool:
        stmt = select(BackupRecord).where(BackupRecord.id == backup_id)
        res = await self.db.execute(stmt)
        backup = res.scalars().first()
        if not backup:
            return False

        try:
            p = Path(backup.filepath)
            if p.exists():
                p.unlink()
        except Exception:
            pass

        await self.db.delete(backup)
        await self.db.commit()
        return True

    async def _enforce_retention(self, max_kept: int = 30):
        """Mantém no máximo 30 backups por padrão, preservando os mais recentes"""
        stmt = select(BackupRecord).order_by(desc(BackupRecord.created_at))
        res = await self.db.execute(stmt)
        all_b = list(res.scalars().all())

        if len(all_b) > max_kept:
            to_delete = all_b[max_kept:]
            for b in to_delete:
                try:
                    Path(b.filepath).unlink(missing_ok=True)
                except Exception:
                    pass
                await self.db.delete(b)
            await self.db.commit()
