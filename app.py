#@author Azrael shi
#@description: a simple web ui for MCP Client, implemented with streamlit
#@createdate 2025/7/16

import streamlit as st
import asyncio
import os
import sys
import threading

from dotenv import load_dotenv
from client import MCPClient

load_dotenv()

class AsyncHelper:
    def __init__(self):
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

    def run_coro(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

def main():
    st.title("MCPClient(Azrael's demo)")

    if 'async_helper' not in st.session_state:
        st.session_state.async_helper = AsyncHelper()

    async_helper = st.session_state.async_helper

    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('DEEPSEEK_API_KEY', '')

    with st.sidebar:
        st.header("配置")
        api_key_input = st.text_input(
            "请输入 DeepSeek API Key:", type="password", value=st.session_state.api_key
        )
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            if 'mcp_client' in st.session_state:
                # 清理旧的client
                client_to_clean = st.session_state.pop('mcp_client')
                async_helper.run_coro(client_to_clean.cleanup())
            st.rerun()

    if not st.session_state.api_key:
        st.info("请输入您的 DeepSeek API Key 开始使用。")
        st.stop()

    if 'mcp_client' not in st.session_state:
        with st.spinner("正在连接到 MCP 服务器..."):
            try:
                server_script_path = os.path.join( "servers","tushareserver.py")
                
                if not os.path.exists(server_script_path):
                    st.error(f"服务器脚本未找到: {server_script_path}")
                    st.stop()

                client = MCPClient(api_key=st.session_state.api_key)
                async_helper.run_coro(client.connect_to_server(server_script_path))
                st.session_state.mcp_client = client
                st.success("已成功连接到 MCP 服务器并准备就绪！")
                
            except Exception as e:
                st.error(f"客户端初始化失败: {e}")
                st.stop()

    client = st.session_state.mcp_client
    
    # 聊天界面
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("请输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    response = async_helper.run_coro(client.process_query(prompt))
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_message = f"处理请求时发生错误: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
        st.rerun()

if __name__ == "__main__":
    main()