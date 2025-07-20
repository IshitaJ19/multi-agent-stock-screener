from fastmcp import Client
import asyncio


async def main() -> None:

    async with Client("http://127.0.0.1:8000/mcp") as client:
        tools = await client.list_tools()

        print(f"Available tools: {tools}")

        print(type(tools))

if __name__ == "__main__":
    asyncio.run(main())