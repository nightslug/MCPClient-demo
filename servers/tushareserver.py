#@author Azrael shi
#@description: revised version of origianl client wilth fully Asynchronous execution
#@create_date 2025/7/21

import tushare as ts
import datetime
import json
import akshare as ak


from typing import Optional
from mcp.server.fastmcp import FastMCP


ts.set_token("0b4b2f62b1b2cebda2e28b8b35fecf9ffcc5fd9fa9e9ae595e3ca27a")
pro = ts.pro_api()
mcp = FastMCP("tushare",log_level="ERROR")

today = datetime.datetime.now().strftime("%Y%m%d")
#查询股票的日线行情
@mcp.tool()
def get_daily_quote(ts_code:str,start_date:str,end_date:str) -> str:
    """查询日线行情
    Args:
        ts_code: Tushare股票代码。单个代码如 '600519.SH'，多个代码请用逗号隔开，如 '600519.SH,000001.SZ'。
        start_date: 开始日期，格式为 YYYYMMDD,例如 '20240101'。
        end_date: 结束日期,格式为YYYYMMDD,例如'20250808'。
    """
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if df.empty:
            return f"查询无结果：未能找到股票代码 {ts_code} 在 {start_date} 到 {end_date} 期间的日线行情数据。"
    return df.to_json(orient = "records" ,force_ascii = False, indent = 4)


#查询ETF的日线行情
@mcp.tool()
def get_daily_fund(ts_code:str,start_date:str,end_date:str) -> str:
    """查询etf行情
    Args:
        ts_code: 基金代码。单个代码如 '510300.SH'，多个代码请用逗号隔开，如 '600519.SH,000001.SZ'。
        start_date: 开始日期，格式为 YYYYMMDD,例如 '20240101'。
        end_date: 结束日期,格式为YYYYMMDD,例如'20250808'。
    """
    df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    if df.empty:
         return f"查询无结果：未能找到股票代码 {ts_code} 在 {start_date} 到 {end_date} 期间的日线行情数据。"
    return df.to_json(orient = "records" ,force_ascii = False, indent = 4)


#获取大宗交易数据
@mcp.tool()
def block_trade(start_date:str,end_date:str,ts_code:Optional[str] = None) -> str:
    """获取大宗交易数据，包括成交价格、成交量、买卖双方营业部等详细信息
    Args:
        start_date: 开始日期，格式为 YYYYMMDD,例如 '20240101'。
        end_date: 结束日期,格式为YYYYMMDD,例如'20250808'。
        ts_code: Tushare股票代码。单个代码如 '600519.SH'，多个代码请用逗号隔开，如 '600519.SH,000001.SZ'。
    """
    df = pro.bond_blk(start_date=start_date, end_date=end_date)
    if ts_code is None:
        if df.empty:
            return f"查询无结果：未能找到在 {start_date} 到 {end_date} 期间的大宗交易数据。"
        return df.to_json(orient = "records" ,force_ascii = False, indent = 4)
    else:
        filtered_df = df[df['ts_code'] == ts_code]
        if filtered_df.empty:
            return f"查询无结果：未能找到股票代码 {ts_code}在 {start_date} 到 {end_date} 期间的大宗交易数据。"
        return df.to_json(orient = "records" ,force_ascii = False, indent = 4)


#获取基金经理的详细信息
@mcp.tool()
def fund_manager_by_name(name:str,ann_date:Optional[str] = None) ->str:
    """根据基金经理姓名查询基金经理详细信息，包括管理的基金列表、个人背景、任职经历等
    Args:
        name: 基金经理姓名，如'张凯'、'刘彦春'等
        ann_date: 公告日期,式为YYYYMMDD,如'20230101'。用于限制查询的公告日期
    """
    params = {
            'name': name
        }
    if ann_date is not None:
        params['ann_date'] = ann_date
    df = pro.fund_manager(**params)
    if df.empty:
        return f"查询无结果：未能找到{name}的信息。"
    return df.to_json(orient = "records" ,force_ascii = False, indent = 4)
    

#获取上市公司前十大股东信息
@mcp.tool()
def find_holders(ts_code:str,start_date:Optional[str]='20250101',end_date:Optional[str]='20252722') ->str:
    """查询上市公司前十大股东信息
    Args:
        name: 公司名称,如‘国金证券’、‘贵州茅台’等
        start_date: 开始日期，格式为 YYYYMMDD,例如 '20240101'
        end_date: 结束日期,格式为YYYYMMDD,例如'20250808'
    """
    df = pro.top10_holders(ts_code=ts_code, start_date=start_date, end_date=end_date)
    return df.to_json(orient = "records" ,force_ascii = False, indent = 4)


def get_news_from_akshare(ts_code: str) -> dict:
    """
    使用AkShare从东方财富网获取特定股票的新闻标题列表。
    此函数能够自动转换代码格式，并健壮地处理返回的数据。

    Args:
        ts_code (str): Tushare格式的股票代码 (例如 '600519.SH' 或 '000001.SZ').

    Returns:
        list: 一个包含新闻标题字符串的列表，如果找不到或出错则返回空列表。
    """

    keyword = ts_code.split('.')[0]

    news_df = ak.stock_news_em(symbol=keyword)
    
    headlines = []
    if not news_df.empty:
        headlines = news_df[['发布时间','新闻标题','新闻内容']].head(15).to_dict()
    return headlines

#预测股票涨跌
@mcp.tool()
def predict_stock_trend(ts_code: str,name:str) -> str:
    """
    为AI准备用于预测股票未来走势的综合数据包。
    此工具会获取指定股票近30天的行情、相关实时新闻,并打包成一个任务JSON交给AI。
    
    Args:
        ts_code: Tushare股票代码,例如 '600519.SH'。
        name: 股票代码对应的名字,例如'贵州茅台'。
    """

    start_date = (datetime.datetime.now()- datetime.timedelta(days = 30)).strftime("%Y%m%d")
    price_history = pro.daily(ts_code=ts_code, start_date=start_date, end_date=today)
    price_history = price_history.to_dict('records')

    news_headlines = get_news_from_akshare(ts_code)    
    

    prompt = f"""
    请你扮演一位专业的金融分析师。以下是你需要分析的数据：
    1.  **股票名称**: {name} ({ts_code})
    2.  **近期价格走势**: 包含近30天的开盘、收盘、最高、最低价和成交量。
    3.  **相关新闻头条**: 最新的市场新闻，可能影响投资者情绪。

    你的任务是：
    1.  **综合分析**: 结合价格数据的技术趋势和新闻数据的基本面/情绪面影响。
    2.  **预测下一个交易日趋势**: 明确给出“看涨”、“看跌”或“震荡盘整”的预测。
    3.  **提供核心依据**: 分点阐述你做出该预测的主要理由，必须从给定的价格和新闻数据中寻找证据。
    4.  **声明**: 在回答末尾必须加上“免责声明:本分析仅为数据展示和AI模型推理,不构成任何投资建议。”
    """

    prompt_package = {
    "status": "Success",
    "data_for_analysis": {
        "price_history": price_history,
        "related_news": news_headlines
    },
    "prompt_for_ai": prompt.strip()
    }
    return json.dumps(prompt_package, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    mcp.run(transport='stdio')
