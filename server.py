from functools import partial

import aiohttp
import anyio
import pymorphy2
from aiohttp import web

from process_article import process_article
from utils import load_charged_dicts


async def handle(request):
    urls = request.query.get('urls')
    if not urls:
        return web.json_response(
            {'error': 'urls query param is required'},
            status=400,
        )

    if len(urls) > 10:
        return web.json_response(
            {'error': 'too many urls in request, should be 10 or less'},
            status=400,
        )

    results = []
    async with aiohttp.ClientSession() as session:
        article_processor = partial(
            process_article,
            session,
            request.app['charged_words'],
            request.app['morph'],
            results,
        )
        async with anyio.create_task_group() as task_group:
            for url in urls.split(','):
                task_group.start_soon(article_processor, url)
    return web.json_response(results)


if __name__ == '__main__':
    app = web.Application()
    app['morph'] = pymorphy2.MorphAnalyzer()
    app['charged_words'] = load_charged_dicts()
    app.add_routes([web.get('/', handle)])
    web.run_app(app)
