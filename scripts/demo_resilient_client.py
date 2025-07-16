import asyncio

from shared.utils.resilience import ResilientClient


async def main():
    async with ResilientClient() as client:
        resp = await client.get("https://api.github.com/repos/openai/gpt-3")
        print(resp.status_code)
        print(resp.json().get("full_name"))


if __name__ == "__main__":
    asyncio.run(main())
