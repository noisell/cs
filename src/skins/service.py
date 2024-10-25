from typing import List, Optional

from fastapi import HTTPException

from src.cases.models import TypePriceCase
from src.repository import skin
from src.skins.models import SkinQuality, RaritySkin
from src.skins.schemas import Sorting, SearchSkinScheme, SkinSimpleScheme, GunsScheme, StatusRes, ResSkinResponseScheme
from src.tasks.task import schedule_task
from src.unit_of_work import UnitOfWork, IUnitOfWork
from src.tasks.redis_manager import task_manager
from difflib import get_close_matches

from src.user.market import main


# noinspection PyArgumentList
class SkinService:

    @classmethod
    async def get_all(
            cls,
            uow: IUnitOfWork,
            limit: int,
            offset: int,
            sorting: Sorting,
            name: str | None = None,
            gun_id: int | None = None,
            quality: SkinQuality | None = None,
            rarity: RaritySkin | None = None,
    ) -> Optional[List[SkinSimpleScheme]]:
        async with uow:
            return await uow.skin.get_all(
                limit=limit, offset=offset, sorting=sorting, name=name, gun_id=gun_id, quality=quality, rarity=rarity,
            )

    @classmethod
    async def add_all_skins(cls):
        async with UnitOfWork() as uow:
            skins = await uow.skin.get_all_names_skins()
        task_manager.add("skins", skins)


    @classmethod
    async def search_by_name(cls, name: str) -> Optional[List[SearchSkinScheme]]:
        skins = task_manager.get("skins")
        skins = {int(key): value.decode('utf-8') for key, value in skins.items()}
        results = []
        for skin_id, skin_name in skins.items():
            if name.lower() in skin_name.lower():
                results.append({'id': skin_id, 'name': skin_name})
        return [SearchSkinScheme.model_validate(result, from_attributes=True) for result in results] if results else None

    @classmethod
    async def get_all_guns(cls, uow: IUnitOfWork) -> List[GunsScheme]:
        async with uow:
            return await uow.gun.get_all_guns()

    @classmethod
    async def get_skin_by_id(cls, uow: IUnitOfWork, skin_id: int) -> SkinSimpleScheme:
        async with uow:
            return await uow.skin.get_skin_by_id(skin_id)

    @classmethod
    async def buy_skin(cls, uow: IUnitOfWork, user_id: int, skin_id: int) -> None:
        async with uow:
            skin = await uow.skin.get_skin_by_id(skin_id)
            user_balance = await uow.user.get_balance_user_full(user_id=user_id, currency=TypePriceCase.usdt)
            if user_balance < skin.price:
                raise HTTPException(status_code=400, detail='Недостаточно средств!')
            await uow.user.update_balance(user_id=user_id, balance_type=TypePriceCase.usdt, value=-skin.price, add=True)
            await uow.user_skin.add({"user_id": user_id, "skin_id": skin.id})
            await uow.commit()

    @classmethod
    async def receiving(cls, uow: IUnitOfWork, user_id: int, skin_id: int) -> ResSkinResponseScheme:
        from src.tasks.receiving import receiving_task
        async with uow:
            user_skin_id = await uow.user_skin.get_skin(user_id=user_id, skin_id=skin_id)
            if user_skin_id is None:
                return ResSkinResponseScheme(status=StatusRes.not_found_skin)
            trade_url = await uow.user.get_trade_url(user_id=user_id)
            if not trade_url:
                return ResSkinResponseScheme(status=StatusRes.not_found_trade_url)
            market_key = await uow.system.get_data("market")
            receiving_id = await uow.user_receiving.add_and_return_id({"user_id": user_id, "skin_id": skin_id, "status": "⌛️ Ожидание принятия обмена"})
            receiving = await main(key_market=market_key, hash_name="name", trade_url=trade_url, receiving_id=receiving_id)
            if receiving != StatusRes.success:
                await uow.user_receiving.delete_receiving(receiving_id=receiving_id)
                return ResSkinResponseScheme(status=receiving)
            await uow.user_skin.delete_skin(skin_id=user_skin_id)
            await uow.commit()
            schedule_task(function=receiving_task, kwargs={"rec_id": receiving_id, "key_market": market_key}, task_id=receiving_id, delay=720)
            return ResSkinResponseScheme(status=StatusRes.success)

    @classmethod
    async def sell_skin(cls, uow: IUnitOfWork, user_id: int, skin_id: int) -> None:
        async with uow:
            user_skin_id = await uow.user_skin.get_skin(user_id=user_id, skin_id=skin_id)
            current_skin = await uow.skin.get_skin_by_id(skin_id=skin_id)
            if user_skin_id is None:
                return None
            await uow.user_skin.delete_skin(skin_id=user_skin_id)
            await uow.user.update_balance(user_id=user_id, balance_type=TypePriceCase.usdt, value=current_skin.price, add=True)
            await uow.commit()
