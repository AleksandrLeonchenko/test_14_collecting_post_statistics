import requests
from bs4 import BeautifulSoup


import aiohttp
from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session

from database import engine
from .models import task


async def parser(link: str):
    """
    Асинхронная функция для разбора веб-страницы и извлечения количества просмотров.

    Args:
        link (str): Ссылка на веб-страницу для анализа.

    Returns:
        dict: Словарь с данными о ссылке, статусе и количестве просмотров.

    """
    status = 2
    print('Задача выполняется: ', link)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(link, headers=headers) as response:
            response_text = await response.text()
            soup = BeautifulSoup(response_text, "html.parser")
            block_list = [
                "post-counters__item",
                "article_layer__simple_footer"
            ]
            for i in block_list:
                block = soup.find("div", {"class": i})
                if block:
                    number_of_views = block.text.split()[0]  # получаем только первое слово из текста
                    status = 3
                    print(number_of_views)
                    print('задача выполнена')
                    break
            else:
                status = 4
                number_of_views = 0
                print('Блок не найден')
    return {'link': link, 'status': status, 'number_of_views': number_of_views if status == 3 else None}


async def views_count(link: str, session: AsyncSession = Depends(get_async_session)):
    """
    Асинхронная функция для подсчета просмотров и записи результатов в базу данных.

    Args:
        link (str): Ссылка на веб-страницу для анализа.
        session (AsyncSession): Асинхронная сессия для взаимодействия с базой данных.

    """
    result = await parser(link)

    link = result['link']
    status = result['status']
    number_of_views = result['number_of_views']

    async with session as db_session:
        stmt = insert(Task).values(link=link, status=status, number_of_views=number_of_views)
        await db_session.execute(stmt)
        await db_session.commit()

