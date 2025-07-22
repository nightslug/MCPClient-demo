import akshare as ak
from pprint import pprint

stock_news_em_df = ak.stock_news_em(symbol="603777")

# 将每一行转为字典并打印
for _, row in stock_news_em_df.iterrows():
    pprint(row.to_dict())