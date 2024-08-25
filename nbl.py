import requests
import pandas as pd
import time
import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

webhook_url = os.getenv("WEBHOOK_URL") # 企微机器人接口
chainShortName, chainId = 'op', 10
tokenContractAddress = '0x4b03afc91295ed778320c2824bad5eb5a1d852dd' # NBL合约地址
minAmount, limit = 3000000, 1 # 最小交易数量&每次获取的交易数
tx_url = f'https://www.oklink.com/api/v5/explorer/token/transaction-list?chainShortName={chainShortName}&\
tokenContractAddress={tokenContractAddress}&minAmount={minAmount}&limit={limit}' # 交易查询url
price_url = f'https://www.oklink.com/api/v5/explorer/tokenprice/market-data?chainId={chainId}\
&tokenContractAddress={tokenContractAddress}' # 币价查询url
chg_url = "https://www.oklink.com/zh-hans/optimism/token/0x4b03afc91295ed778320c2824bad5eb5a1d852dd"
port = os.getenv("PORT")
proxy = {'https': f'http://127.0.0.1:{port}', 'http': f'http://127.0.0.1:{port}'}
oklink_headers = {'Ok-Access-Key': os.getenv("OK_ACCESS_KEY")}
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
address = pd.read_excel('地址标记_测试.xlsx', index_col=False)

# 发送信息至企业微信
def send_msg(transaction, price, chg):
    num = len(address.index) # 已标记地址数
    txhash = transaction['txid'] # 交易哈希
    From = transaction['from'] # 转出地址
    To = transaction['to'] # 转入地址
    amount = float(transaction['amount']) # 转账数量
    now = time.time()
    transactionTime = transaction['transactionTime'][:-3] # 交易时间戳
    timeArray = time.localtime(int(transactionTime))
    txTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print('当前价格：', f'{price:.8f}', '涨跌幅：', chg)
    print('当前时间', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(now))))
    if From not in list(address['address']):
        address.loc[len(address)]= [From, '未标记地址']
    if To not in list(address['address']):
        address.loc[len(address)]= [To, '未标记地址']
    info = {
            "content": f"# `检测到NBL大额转账!(测试版1.1)`\n\
转出地址：<font color='comment'>{From}<font color='red'>({address[address['address'] == From].iloc[0, 1]})</font></font>\n\
转入地址：<font color='comment'>{To}<font color='red'>({address[address['address'] == To].iloc[0, 1]})</font></font>\n\
转入数量💰：<font color='Orange'>{format(int(amount), ',')}(${round(amount * price, 2)})</font>\n\
交易哈希🔍：[{txhash}](https://platform.arkhamintelligence.com/explorer/tx/{txhash})\n\
交易时间⏱️：<font color='comment'>{txTime}</font>\n\
当前币价{'📈' if float(chg[:-1]) >= 0 else '📉'}：{price:.8f}\
(<font color={'red' if float(chg[:-1]) >= 0 else 'green' }>{chg}</font>)"
           }
    msg = {
       "msgtype": "markdown",
       "agentid" : 1,
       "markdown": info,
       "enable_duplicate_check": 1,
       "duplicate_check_interval": 300
    }
    data = json.dumps(msg)
    if int(now) - int(transactionTime) < 300: #交易的时间发生在5分钟内
        result = requests.post(webhook_url, data=data, proxies=proxy)
    address.drop(index=[i for i in range(num, len(address))])
    

# 代币大额交易查询
def get_txlist():
    tx_response = requests.get(tx_url, headers=oklink_headers, proxies=proxy) # 交易查询返回
    transactionList = tx_response.json()['data'][0]['transactionList']
    return transactionList

# NBL价格查询
def get_price():
    price_response = requests.get(price_url, headers=oklink_headers, proxies=proxy) # 币价查询返回
    nbl_price = float(price_response.json()['data'][0]['lastPrice'])
    return nbl_price

# NBL价格涨跌幅查询
def get_chg():
    response = requests.get(chg_url, headers=headers, proxies=proxy)
    soup = BeautifulSoup(response.text, 'html.parser')
    chg = soup.find(class_ = 'index_changes__BSNp- index_red__-eI0m').text
    return chg