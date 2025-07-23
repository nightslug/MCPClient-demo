#@author Azrael shi
#@description: revised version of origianl client wilth fully Asynchronous execution
#@create_date 2025/7/16

import asyncio
import os
import json
import sys
from datetime import datetime
from typing import Optional
from contextlib import AsyncExitStack
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

class MCPClient:
    def __init__(self, api_key: str):
        self.exit_stack = AsyncExitStack()
        self.deepseek_api_key = api_key
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL")
        # 使用 AsyncOpenAI 异步版本
        self.client = AsyncOpenAI(api_key=self.deepseek_api_key, base_url=self.base_url)
        self.session: Optional[ClientSession] = None

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")

        command = sys.executable if is_python else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path])
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        
        response = await self.session.list_tools()
        print("\n已连接到服务器,支持以下工具:", [tool.name for tool in response.tools])

    async def process_query(self, query: list) -> str:
        messages = query
        # Add current time to environment details
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S (%Z, UTC%z)")
        messages.append({
            "role": "system",
            "content": f"Current Time: {current_time}"
        })
        
        list_tools_response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in list_tools_response.tools]

        # 使用 await 进行异步调用
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=available_tools
        )
        
        choice = response.choices[0]
        if choice.finish_reason == "tool_calls":
            tool_call = choice.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            result = await self.session.call_tool(tool_name, tool_args)
            print(f"\n[Calling tool {tool_name} with args {tool_args}]\n")
            
            messages.append(choice.message.model_dump())
            messages.append({
                "role": "tool",
                "content": result.content[0].text,
                "tool_call_id": tool_call.id,
            })
            
            # 使用 await 进行第二次异步调用
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return final_response.choices[0].message.content
            
        return choice.message.content

    async def cleanup(self):
        print("Cleaning up MCP client resources...")
        await self.exit_stack.aclose()
        print("Cleanup complete.")
