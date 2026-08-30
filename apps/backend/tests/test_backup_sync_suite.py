import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import engine, Base, async_session_maker
from app.services.backup_manager import BackupManager
from app.services.sync_manager import SyncManager, ConnectivityService
from app.core.backup_encryption import BackupEncryption
from app.models.backup_sync import BackupType

@pytest.mark.asyncio
async def test_backup_encryption_and_checksum():
    raw_data = b"Resolva database binary stream test 2026"
    encrypted = BackupEncryption.encrypt_bytes(raw_data)
    assert encrypted != raw_data

    decrypted = BackupEncryption.decrypt_bytes(encrypted)
    assert decrypted == raw_data

@pytest.mark.asyncio
async def test_backup_manager_flow():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        manager = BackupManager(session)

        # 1. Criação
        backup = await manager.create_backup(backup_type=BackupType.MANUAL)
        assert backup.id is not None
        assert backup.size_bytes >= 0
        assert len(backup.checksum_sha256) == 64

        # 2. Listagem
        backups = await manager.list_backups()
        assert len(backups) > 0

        # 3. Restore sem confirmação deve falhar
        success_unconf, msg_unconf = await manager.restore_backup(backup.id, confirmed=False)
        assert success_unconf == False

        # 4. Restore com confirmação
        success, msg = await manager.restore_backup(backup.id, confirmed=True)
        assert success == True

@pytest.mark.asyncio
async def test_sync_manager_and_connectivity():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        sync_mgr = SyncManager(session)

        status = await sync_mgr.get_sync_status()
        assert "device_id" in status
        assert "connectivity_status" in status
        assert "pending_queue_count" in status

        # Enfileirar mutação offline
        item = await sync_mgr.enqueue_operation(
            entity_type="task",
            entity_id="101",
            operation="CREATE",
            payload={"title": "Tarefa offline", "password_leak_prevention": "secret"}
        )
        assert item.id is not None
        assert "password_leak_prevention" not in item.payload

        # Processar fila
        succ, fails = await sync_mgr.process_queue()
        assert succ >= 1

@pytest.mark.asyncio
async def test_backup_sync_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Status de sincronização
        res_sync = await ac.get("/api/sync/status")
        assert res_sync.status_code == 200
        assert "connectivity_status" in res_sync.json()

        # Criar backup via API
        res_b = await ac.post("/api/backups", json={"backup_type": "MANUAL"})
        assert res_b.status_code == 201
        b_data = res_b.json()
        b_id = b_data["id"]

        # Listar backups
        res_list = await ac.get("/api/backups")
        assert res_list.status_code == 200
        assert len(res_list.json()) > 0

        # Disparar sincronização
        res_start = await ac.post("/api/sync/start")
        assert res_start.status_code == 200
