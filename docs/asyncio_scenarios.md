# Common asyncio scenarios

This guide demonstrates how to integrate blocking code, migrate to async libraries, work in interactive environments and deploy with Gunicorn + Uvicorn.

## 1. Integrating blocking code

Use `loop.run_in_executor()` to offload a blocking function to a thread pool. The event loop can continue processing other tasks.

```python
import asyncio
import time


def blocking_task():
    print("Starting blocking task...")
    time.sleep(3)
    print("Blocking task done.")
    return "result"


async def main():
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(None, blocking_task)
    print("Waiting for result...")
    for i in range(3):
        await asyncio.sleep(1)
        print(f"tick {i}")
    result = await future
    print("Result:", result)


asyncio.run(main())
```

## 2. Refactoring to native async I/O

Replace `requests` and `open()` with their async counterparts (`aiohttp`, `aiofiles`).

```python
import aiohttp
import aiofiles
import asyncio


async def fetch_and_save(url, path):
    async with aiohttp.ClientSession() as session:
        async with index(url) as resp:
            html = await resp.text()
    async with aiofiles.open(path, "w") as f:
        await f.write(html)


asyncio.run(fetch_and_save("https://example.com", "out.html"))
```

## 3. Interactive environments

Jupyter and IPython run an event loop already. Patch it with `nest_asyncio` for quick experiments, **but avoid this in production**. Patching the loop can lead to deadlocks or tasks that never run. Instead, restructure your code to use a single, well-controlled event loop.

```python
import asyncio
import nest_asyncio

nest_asyncio.apply()

async def demo():
    await asyncio.sleep(1)
    print("done")

asyncio.run(demo())
```

## 4. Production deployment

Combine Gunicorn and Uvicorn for scalable ASGI apps.

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Gunicorn manages multiple processes (parallelism) while each Uvicorn worker runs the asyncio event loop (concurrency).
