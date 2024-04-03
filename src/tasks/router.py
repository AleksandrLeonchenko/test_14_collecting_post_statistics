import asyncio
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session, engine
from .schemas import LinksRequest
from .tasks import parser, views_count
from .models import task

router = APIRouter(prefix="/views")


async def process_link_with_timeout(link):
    try:
        await asyncio.wait_for(views_count(link), timeout=5)
        print(f"Task for link completed successfully.")
    except asyncio.TimeoutError:
        print(f"Task for link {link} timed out.")

# async def process_link_with_timeout(link: str):
#     async with get_async_session() as session:
#         await asyncio.wait_for(parser(link, session), timeout=5)


@router.post("/process_links/")
async def process_links(links_request: LinksRequest, background_tasks: BackgroundTasks):
    links = links_request.links

    for link in links:
        status = 1
        print('Задача получена: ', link, 'status', status)
        background_tasks.add_task(process_link_with_timeout, link)

    return {"message": f"Received links: {links}"}


@router.get("/last_tasks/")
async def get_last_tasks():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Выбираем последние 10 записей из таблицы task
            stmt = select(task).order_by(task.id.desc()).limit(10)
            result = await session.execute(stmt)
            tasks = result.scalars().all()
            task_data = [{"link": task.link, "number_of_views": task.number_of_views} for task in tasks]

            return task_data