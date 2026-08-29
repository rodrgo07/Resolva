from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.schemas.settings import SettingResponse, SettingUpdate
from app.models.settings import AppSetting

router = APIRouter()

@router.get("/", response_model=List[SettingResponse])
async def get_settings(db: AsyncSession = Depends(get_db)):
    query = select(AppSetting)
    result = await db.execute(query)
    return list(result.scalars().all())

@router.get("/{key}", response_model=SettingResponse)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    query = select(AppSetting).where(AppSetting.key == key)
    result = await db.execute(query)
    setting = result.scalars().first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/{key}", response_model=SettingResponse)
async def update_setting(key: str, setting_in: SettingUpdate, db: AsyncSession = Depends(get_db)):
    query = select(AppSetting).where(AppSetting.key == key)
    result = await db.execute(query)
    setting = result.scalars().first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
        
    update_q = update(AppSetting).where(AppSetting.key == key).values(
        value=setting_in.value
    ).returning(AppSetting)
    result = await db.execute(update_q)
    await db.commit()
    return result.scalars().first()
