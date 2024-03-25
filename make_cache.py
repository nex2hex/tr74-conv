import asyncio
import pickle
from contextlib import closing

import aiohttp

from app.settings import ROUTES_DATAFRAME_CACHE, ROUTES_FILE, ROUTES_LINK, STOPS_FILE, STOPS_LINK
from app.utils import _get_routes_dataframe


async def download_remote_files():
    async with aiohttp.ClientSession() as session:
        async with session.get(ROUTES_LINK) as response:
            assert response.status == 200
            ROUTES_FILE.write_bytes(await response.read())

        async with session.get(STOPS_LINK) as response:
            assert response.status == 200
            STOPS_FILE.write_bytes(await response.read())


if __name__ == "__main__":
    ROUTES_FILE.unlink(missing_ok=True)
    STOPS_FILE.unlink(missing_ok=True)

    with closing(asyncio.new_event_loop()) as loop:
        result = loop.run_until_complete(download_remote_files())

    r = _get_routes_dataframe(ttl_hash=0, cached=False)
    ROUTES_DATAFRAME_CACHE.write_bytes(pickle.dumps(r))
