import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import matplotlib.pyplot as plt
import seaborn as sns


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

tickers = [
    "COIN",
    "TSLA",
    "ABEV",
    "AAPL",
    "ZLAB",
    "BMBL",
    "RLX",
    "IOT",
    "QQQM",
    "GNS",
    "TXT",
    "DE",
    "CEIX",
    "BBY",
    "ABT",
    "KALA",
    "AGCO",
    "ABR",
    "VOO",
    "GERN",
]  # 20 компаний для парсинга


def load_data(url):  # парсинг данных
    r = requests.get(url, headers=header)
    data = pd.read_html(r.text)
    return data


print("Идет парсинг данных...")
st = time.time()
df = pd.DataFrame(columns=["name", "open", "last"])  # создаю датафрейм для табло
for ticker in tickers:
    print(ticker, "в процессе...")
    yahoo_url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"  # парсинг идёт с finance.yahoo.com
    try:  # запрашиваю open_price
        summary_data = load_data(yahoo_url)
        open_price = float(summary_data[0][1][1])
    except:
        summary_data = load_data(yahoo_url)
        print(ticker, "open")
        open_price = 0.00  # в случае ошибки пишу 0
    finiz_url = (
        f"https://finviz.com/quote.ashx?t={ticker}&p=d"  # парсинг идёт с finviz.com
    )
    try:  # запрашиваю last_price
        summary_data = load_data(finiz_url)
        last_price = float(summary_data[5][0][0].split()[-7].lstrip("Price"))
    except:
        print(ticker, "last")
        last_price = 0.00  # в случае ошибки пишу 0
    df.loc[df.shape[0]] = [ticker, open_price, last_price]
    time.sleep(random.random() * 3)  # пауза для сокрытия факта парсинга

df = df[::-1]
df.to_csv("static/csv/tablo.csv", index=False)

d100 = pd.DataFrame(columns=tickers)
for ticker in tickers:
    historiscal_url = f"https://finance.yahoo.com/quote/{ticker}/history?p={ticker}"
    historiscal_data = load_data(historiscal_url)
    data = historiscal_data[0]
    d100[ticker] = data.Open
    time.sleep(random.random() * 3)

d100 = d100.drop(labels=[100], axis=0)

for i in d100:  # обрабатываю и очищаю данные
    try:
        d100[i] = d100[i].astype("float64")  # перевожу во float
    except:
        new_list = []
        for j in range(len(d100[i])):
            try:
                new_list.append(float(d100[i][j]))
            except:
                new_list.append(float(d100[i][j - 1]))
        d100[i] = new_list

for i in d100:  # заполняю пропуски
    d100[i] = d100[i].fillna(d100[i].mean())

d100 = d100[::-1]
d100.to_csv("static/csv/d100.csv", index=False)

print("Парсинг занял:", time.time() - st)
