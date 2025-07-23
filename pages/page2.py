#@author Azrael shi
#@description: a simple web ui for MCP Client, implemented with streamlit
#@create_date 2025/7/23

import streamlit as st

st.page_link("app.py", label="⬅️ 返回主页面")


def local_css():
    st.markdown("""
        <style>
        /* Tool Card: 每一个工具的最外层白色卡片 */
        .tool-card {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: box-shadow 0.3s ease-in-out;
            height: 100%; 
            display: flex; 
            flex-direction: column;
            height: 400px;    
            overflow-y: auto; 
        }
        .tool-card:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        }
        .tool-content {
             flex-grow: 1;
        }
        .tool-header { font-size: 1.1em; font-weight: 600; color: #2c3e50; margin-bottom: 8px; }
        .tool-description { font-size: 1em; color: #576574; margin-bottom: 20px; }
        .param-box { background-color: #f8f9fa; border-left: 5px solid #3498db; border-radius: 8px; padding: 15px; margin-bottom: 12px; }
        .param-header { display: flex; align-items: center; margin-bottom: 8px; }
        .param-name { font-weight: 600; color: #34495e; margin-right: 8px; }
        .tag-optional { background-color: #e8f5e9; color: #2e7d32; padding: 3px 8px; border-radius: 5px; font-size: 0.75em; font-weight: 600; }
        .tag-required { background-color: #fff3e0; color: #ef6c00; padding: 3px 8px; border-radius: 5px; font-size: 0.75em; font-weight: 600; }
        .param-desc { font-size: 0.75em; color: #576574; }
        .param-type { font-size: 0.7em; color: #8395a7; margin-top: 8px; }
        
        </style>
    """, unsafe_allow_html=True)


def create_tool_card(icon, name, description, params):
    params_html_parts = []
    for p in params:
        tag_class = "tag-optional" if p['tag'] == '可选' else "tag-required"
        part = f'''<div class="param-box">
                    <div class="param-header">
                        <span class="param-name">{p['name']}</span>
                        <span class="{tag_class}">{p['tag']}</span>
                    </div>
                    <div class="param-desc">{p['desc']}</div>
                    <div class="param-type">类型: {p['type']}</div>
                </div>'''
        params_html_parts.append(part)
    params_html = "".join(params_html_parts)
    card_html = f'''<div class="tool-card">
            <div class="tool-content">
                <div class="tool-header">{icon} {name}</div>
                <div class="tool-description">{description}</div>
                <strong>参数列表:</strong>
                {params_html}
            </div>
        </div>'''
    st.markdown(card_html, unsafe_allow_html=True)

tools_data = [
    {
        "icon": "📈", "name": "get_daily_quote",
        "description": "查询股票的日线行情数据。",
        "params": [
            {"name": "ts_code", "tag": "必需", "desc": "Tushare股票代码。单个代码如 '600519.SH'，多个用逗号隔开。", "type": "string"},
            {"name": "start_date", "tag": "必需", "desc": "开始日期，格式为 YYYYMMDD, 例如 '20240101'。", "type": "string"},
            {"name": "end_date", "tag": "必需", "desc": "结束日期，格式为 YYYYMMDD, 例如 '20250721'。", "type": "string"}
        ]
    },
    {
        "icon": "📊", "name": "get_daily_fund",
        "description": "查询ETF基金的日线行情数据。",
        "params": [
            {"name": "ts_code", "tag": "必需", "desc": "基金代码。单个代码如 '510300.SH'，多个用逗号隔开。", "type": "string"},
            {"name": "start_date", "tag": "必需", "desc": "开始日期，格式为 YYYYMMDD, 例如 '20240101'。", "type": "string"},
            {"name": "end_date", "tag": "必需", "desc": "结束日期，格式为 YYYYMMDD, 例如 '20250721'。", "type": "string"}
        ]
    },
    {
        "icon": "⚙️", "name": "index_data",
        "description": "获取指定股票指数的数据，例如上证指数、深证成指等",
        "params": [
            {"name": "code", "tag": "必需", "desc": "指数代码，如’000001.SH‘表示上证指数，’399001.SZ‘表示深证成指", "type": "string"},
            {"name": "start_date", "tag": "必需", "desc": "起始日期，格式为YYYYMMDD，如’20230101‘", "type": "string"},
            {"name": "end_date", "tag": "必需", "desc": "结束日期，格式为YYYYMMDD，如’20230131‘", "type": "string"},
        ]
    },
    {
        "icon": "💼", "name": "block_trade",
        "description": "获取大宗交易数据，包括成交价格、成交量、买卖双方营业部等详细信息。",
        "params": [
            {"name": "start_date", "tag": "必需", "desc": "开始日期，格式为 YYYYMMDD, 例如 '20240101'。", "type": "string"},
            {"name": "end_date", "tag": "必需", "desc": "结束日期，格式为 YYYYMMDD, 例如 '20250721'。", "type": "string"},
            {"name": "ts_code", "tag": "可选", "desc": "Tushare股票代码。若提供，则只查询该股票的数据。", "type": "string"},
        ]
    },
    {
        "icon": "🧑‍💼", "name": "fund_manager_by_name",
        "description": "根据姓名查询基金经理详细信息，包括管理的基金列表、个人背景、任职经历等。",
        "params": [
            {"name": "name", "tag": "必需", "desc": "基金经理姓名，例如 '张坤'、'刘彦春'。", "type": "string"},
            {"name": "ann_date", "tag": "可选", "desc": "公告日期，格式为 YYYYMMDD。用于查询特定日期的经理信息。", "type": "string"}
        ]
    },
    {
        "icon": "👥", "name": "find_holders",
        "description": "查询上市公司的前十大股东信息。",
        "params": [
            {"name": "ts_code", "tag": "必需", "desc": "Tushare股票代码，例如 '600519.SH'。", "type": "string"},
            {"name": "start_date", "tag": "可选", "desc": "开始日期，格式为 YYYYMMDD。", "type": "string"},
            {"name": "end_date", "tag": "可选", "desc": "结束日期，格式为 YYYYMMDD。", "type": "string"}
        ]
    },
    {
        "icon": "🔮", "name": "predict_stock_trend",
        "description": "为AI准备用于预测股票未来走势的综合数据包。此工具会获取指定股票近30天的行情和相关实时新闻。",
        "params": [
            {"name": "ts_code", "tag": "必须", "desc": "Tushare股票代码，例如 '600519.SH'。", "type": "string"},
            {"name": "name", "tag": "必须", "desc": "股票代码对应的名称，例如 '贵州茅台'。", "type": "string"}
        ]
    }
]


st.set_page_config(page_title="工具列表", layout="wide")

local_css()

left_spacer, content_column, right_spacer = st.columns([2, 9, 2])

with content_column:
    with st.expander(f"🔗 tushare-server ({len(tools_data)} 个工具)", expanded=True):
        cols = st.columns(2) 
        for i, tool in enumerate(tools_data):
            with cols[i % len(cols)]:
                create_tool_card(tool["icon"], tool["name"], tool["description"], tool["params"])