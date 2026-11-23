import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["hsk_mcp_server.py"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()          # 第一步：发现
            print([t.name for t in tools.tools])  # ['hsk_level', 'list_by_level', 'count_by_level']
            res = await s.call_tool("hsk_level", {"word": "把"})   # 第二步：调用
            print(res.content[0].text)            # 把 -> 3 级
            res2 = await s.call_tool("count_by_level", {"level": "3"})
            print(res2.content[0].text)           # 3 级共 N 个词

asyncio.run(main())
