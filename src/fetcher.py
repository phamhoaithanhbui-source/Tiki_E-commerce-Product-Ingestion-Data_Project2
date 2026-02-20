import aiohttp
import asyncio
from config import (
    BASE_URL,
    HEADERS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    CONCURRENCY_LIMIT,
    CHUNK_SIZE
)

SEM = asyncio.Semaphore(CONCURRENCY_LIMIT)

async def fetch_product(session, product_id, retries=3):
    url = BASE_URL.format(product_id)

    async with SEM:
        for attempt in range(retries):
            try:
                async with session.get(
                    url,
                    headers=HEADERS,
                    timeout=5
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data,
                            "error": None,
                            "id": product_id
                        }

                    if response.status == 404:
                        return {
                            "success": False,
                            "data": None,
                            "error": "Not Found (404)",
                            "id": product_id
                        }

                    if response.status == 429:
                        # Exponential backoff
                        await asyncio.sleep(2 ** attempt)
                        continue

                    return {
                        "success": False,
                        "data": None,
                        "error": f"HTTP {response.status}",
                        "id": product_id
                    }

            except asyncio.TimeoutError:
                await asyncio.sleep(2 ** attempt)

            except aiohttp.ClientError as e:
                return {
                    "success": False,
                    "data": None,
                    "error": f"ClientError: {str(e)}",
                    "id": product_id
                }

        return {
            "success": False,
            "data": None,
            "error": "Max retries exceeded",
            "id": product_id
        }


async def fetch_batch(product_ids):

    timeout = aiohttp.ClientTimeout(total=10)

    connector = aiohttp.TCPConnector(
        limit=60,
        ttl_dns_cache=300,
        keepalive_timeout=30
    )

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector
    ) as session:

        results = []

        # CHUNK PROCESSING
        for i in range(0, len(product_ids), CHUNK_SIZE):

            chunk = product_ids[i:i + CHUNK_SIZE]

            tasks = [
                fetch_product(session, pid)
                for pid in chunk
            ]

            chunk_results = await asyncio.gather(*tasks)

            results.extend(chunk_results)

        return results