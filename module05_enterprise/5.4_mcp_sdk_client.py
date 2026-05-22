import asyncio

from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client

SERVER = "http://localhost:8000/mcp"


async def main():
    async with streamable_http_client(SERVER) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            result = await session.call_tool("get_weather", {"city": "London"})
            print("Weather:", result.content[0].text if result.content else result.structuredContent)

            result = await session.call_tool("calculate", {"expression": "12 * 8 + 5"})
            print("Math:", result.content[0].text if result.content else result.structuredContent)

            result = await session.call_tool("describe_city", {"city": "Tokyo"})
            print("City:", result.content[0].text if result.content else result.structuredContent)

            resources = await session.list_resources()
            print("Resources:", [str(r.uri) for r in resources.resources])

            content = await session.read_resource("data://cities")
            block = content.contents[0]
            print("Cities:", block.text if isinstance(block, types.TextResourceContents) else block)

            content = await session.read_resource("data://city/Tokyo")
            block = content.contents[0]
            print("Detail:", block.text if isinstance(block, types.TextResourceContents) else block)

            prompts = await session.list_prompts()
            print("Prompts:", [p.name for p in prompts.prompts])

            prompt = await session.get_prompt("weather_prompt", {"city": "Tokyo"})
            print("Prompt text:", prompt.messages[0].content.text)


if __name__ == "__main__":
    asyncio.run(main())
