from src.bot.handlers.system import receiving_message
from src.unit_of_work import UnitOfWork
from src.user.market import get_info

async def receiving_task(rec_id: int, key_market: str):
    async with UnitOfWork() as uow:
        rec = await get_info(rec_id=rec_id, key_market=key_market)
        receiving = await uow.user_receiving.get_by_id(rec_id=rec_id)
        if rec is False or rec == "5":
            # Возврат скина
            await uow.user_receiving.update_status(receiving_id=rec_id, status="❗️ Срок действия истек")
            await uow.user_skin.add(data={"user_id": receiving.user_id, "skin_id": receiving.skin_id})
            await receiving_message(user_id=receiving.user_id, success=False)
        else:
            # Завершение сделки
            await uow.user_receiving.update_status(receiving_id=rec_id, status="✅ Обмен успешно принят")
            await receiving_message(user_id=receiving.user_id, success=False)