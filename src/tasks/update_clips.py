from src.bot.handlers.system import clip_message
from src.tasks.task import schedule_task
from src.unit_of_work import UnitOfWork


async def update_clip(user_id: int):
    async with UnitOfWork() as uow:
        user = await uow.user.get_main_info(user_id=user_id)
        if user.count_clip == 9:
            await uow.user.update_clip(user_id=user_id, minus=False)
            await clip_message(user_id=user_id)
        else:
            await uow.user.update_clip(user_id=user_id, minus=False)
            schedule_task(function=update_clip, kwargs={'user_id': user_id}, task_id=user_id, delay=3600)
