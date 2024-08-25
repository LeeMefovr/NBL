from nbl import *
from bs4 import BeautifulSoup

while True:
    transactionlist = get_txlist()
    nbl_price = get_price()
    chg = get_chg()
    for transaction in transactionlist:
        send_msg(transaction, nbl_price, chg)
    time.sleep(300)