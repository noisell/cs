import logging
import asyncio
import json
import time
from typing import Callable, Awaitable
from src.tasks.redis_manager import task_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def schedule_task(function: Callable, kwargs: dict, task_id: int, delay: int = 0):
    task_data = {
        'function': function.__name__,
        'kwargs': json.dumps(kwargs),
        'execution_time': time.time() + delay
    }
    task_manager.add(name=f"task:{task_id}", mapping=task_data)


async def run_task(task_data:  Awaitable[dict] | dict):
    from src.tasks.update_clips import update_clip
    from src.tasks.bets import pay
    from src.tasks.receiving import receiving_task
    try:
        task_func = eval(task_data[b'function'])
        kwargs = json.loads(task_data[b'kwargs'])
        asyncio.create_task(task_func(**kwargs))
        logger.info(f"Задача выполняется")
    except KeyError as e:
        logger.error(f"Ошибка ключей при выполнении задачи: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при выполнении задачи: {e}")


async def main():
    logger.info("Сервис задач запущен.")
    while True:
        await asyncio.sleep(1)
        keys = task_manager.keys("task:*")
        if keys:
            for key in keys:
                task_data = task_manager.get(name=key.decode())
                execution_time = float(task_data[b'execution_time'])
                if time.time() >= execution_time:
                    await run_task(task_data)
                    task_manager.delete(key.decode())
                    logger.info(f"Задача удалена")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Сервис задач остановлен.")