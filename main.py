from flask import Flask, render_template, app, url_for
import csv
import matplotlib.pyplot as plt
import pandas as pd
import atexit
import os
import create_plots
import warnings
import torch
from aniemore.recognizers.text import TextRecognizer
from aniemore.models import HuggingFaceModel
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from datetime import date, datetime, timedelta
from bisect import bisect
from flask import request
import pickle


with open("cat1.pkl", "rb") as f:
    cat1 = pickle.load(f)

with open("cat2.pkl", "rb") as f:
    cat2 = pickle.load(f)


warnings.filterwarnings("ignore")


app = Flask(__name__)

PORT = 8080
HOST = "127.0.0.1"

model = HuggingFaceModel.Text.Bert_Tiny2
device = "cuda" if torch.cuda.is_available() else "cpu"
tr = TextRecognizer(model=model, device=device)


def get_fon():
    fon = 0
    url = "https://www.rbc.ru/economics/"
    r = requests.get(url, UserAgent().chrome)
    soup = BeautifulSoup(r.content, "html.parser")
    for irt in soup.findAll(
        "a", {"class": "item__link rm-cm-item-link js-rm-central-column-item-link"}
    ):
        r = requests.get(irt["href"], UserAgent().chrome)
        soup2 = BeautifulSoup(r.content, "html.parser")
        q = ""
        for i in soup2.findAll("p"):
            q += i.text
        dic = tr.recognize(q, return_single_label=False)
        if dic["happiness"] > dic["sadness"]:
            fon += 1
        else:
            fon -= 1

    if fon > 0:
        return "Новостной фон положительный, рекомендовано закупать более волативные активы"
    return "Новостной фон отрицательный, рекомендовано закупать защитные активы"


def get_price(want_date, company):
    dic = {
        "GBP": 1035,  # Фунт стерлингов Соединенного королевства
        "USD": 1235,  # Доллар США
        "EUR": 1239,  # Евро
        "CNY": 1375,  # Юань
    }
    want_date = date(*reversed(list(map(int, want_date.split(".")))))
    if datetime.now().date() >= want_date:
        if company in dic.keys():
            return parse_money(want_date, company)
        return parse_stoks(want_date, company)
    if company in dic.keys():
        return predict_money(want_date, company)
    return predict_stoks(want_date, company)


def couple_money(want_date, name1, name2):
    c1 = parse_money(want_date, name1)
    c2 = parse_money(want_date, name2)
    return c1 / c2


def parse_money(want_date, name):
    dic = {
        "GBP": 1035,  # Фунт стерлингов Соединенного королевства
        "USD": 1235,  # Доллар США
        "EUR": 1239,  # Евро
        "CNY": 1375,  # Юань
    }

    next_date = date(*reversed(list(map(int, str(want_date).split("-")))))
    next_date += timedelta(days=1)

    day = str(next_date.day)
    if len(day) == 1:
        day = "0" + day
    month = str(next_date.month)
    if len(month) == 1:
        month = "0" + month

    next_date = day + "." + month + "." + str(next_date.year)

    url = f"https://www.cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.so=1&UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.VAL_NM_RQ=R0{dic[name]}&UniDbQuery.From={want_date}&UniDbQuery.To={next_date}"
    r = requests.get(url, UserAgent().chrome)
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find("div", {"class": "table"})
    s = table.findAll("tr")[2:]
    q = s[-1].findAll("td")
    count = int(q[1].text)
    cost = float(q[2].text.replace(",", ".")) / count
    return cost


def parse_stoks(want_date, name):
    dic = {
        "GMKN": "https://ru.investing.com/equities/gmk-noril-nickel_rts-historical-data",
        "GAZP": "https://ru.investing.com/equities/gazprom_rts-historical-data",
        "SBER": "https://ru.investing.com/equities/sberbank_rts-historical-data",
        "AFLT": "https://ru.investing.com/equities/aeroflot-historical-data",
        "AAPL": "https://ru.investing.com/equities/apple-computer-inc-historical-data",
        "VTBR": "https://ru.investing.com/equities/vtb_rts-historical-data",
        "LKOH": "https://ru.investing.com/equities/lukoil_rts-historical-data",
        "BA": "https://ru.investing.com/equities/boeing-co-historical-data",
        "INTC": "https://ru.investing.com/equities/intel-corp-historical-data",
        "MSFT": "https://ru.investing.com/equities/microsoft-corp-historical-data",
        "JPM": "https://ru.investing.com/equities/jp-morgan-chase-historical-data",
        "GS": "https://ru.investing.com/equities/goldman-sachs-group-historical-data",
        "KO": "https://ru.investing.com/equities/coca-cola-co-historical-data",
        "MCD": "https://ru.investing.com/equities/mcdonalds-historical-data",
        "AMZN": "https://ru.investing.com/equities/amazon-com-inc-historical-data",
        "ADSGn": "https://ru.investing.com/equities/adidas-salomon-historical-data",
        "SIEGn": "https://ru.investing.com/equities/siemens-historical-data",
        "DBKGn": "https://ru.investing.com/equities/deutsche-bank-historical-data",
        "HNKG_p": "https://ru.investing.com/equities/henkel-hgaa-vz-historical-data",
        "BMWG": "https://ru.investing.com/equities/bay-mot-werke-historical-data",
    }

    r = requests.get(dic[name])
    df = pd.read_html(r.content)
    df[1].columns = "date,last,open,max,min,volume,delta".split(",")
    s = []
    for i in df[1]["volume"]:
        i = str(i)
        if i[-1] == "M":
            s.append(float(i[:-1].replace(",", ".")) * 10**6)
        elif i[-1] == "K":
            s.append(float(i[:-1].replace(",", ".")) * 10**3)
        elif i[-1] == "B":
            s.append(float(i[:-1].replace(",", ".")) * 10**9)
        else:
            s.append(float(i.replace(",", ".")))
    df[1].volume = s
    alll = list(df[1]["last"])[0]
    try:
        return float(
            str(list(df[1].loc[df[1].date == want_date]["last"])[0])
            .replace(".", "")
            .replace(",", ".")
        )
    except:
        # try:
        #     s = [date(*reversed(list(map(int, i.split("."))))) for i in df[1].date]
        #     print(s)
        #     print(list(df[1]['date'])[bisect(s, date(*reversed(list(map(int, want_date.split("."))))))])
        #     return float(str(list(df[1]['last'])[bisect(s, date(*reversed(list(map(int, want_date.split("."))))))]).replace('.', '').replace(',', '.'))
        # except:
        df = pd.read_csv("static/csv/" + name + ".csv")
        try:
            # print(list(df.loc[df.date == want_date]['last'])[0])
            return list(df.loc[df.date == want_date]["last"])[0]
        except:
            try:
                s = [date(*reversed(list(map(int, i.split("."))))) for i in df.date]
                return list(df["last"])[
                    bisect(s, date(*reversed(list(map(int, want_date.split("."))))))
                ]
            except:
                return alll


def predict_stoks(want_date, name):
    ann = []
    delta = (
        date(*reversed(list(map(int, want_date.split("."))))) - datetime.now().date()
    )
    delta = delta.days
    q, s = parse_stoks_last_60(name)
    for i in range(delta):
        p1 = cat1.predict(s)
        p2 = cat2.predict(s)
        q *= p1
        s.pop(0)
        s[59] = p1
        s.append(p2)
        ann.append(q)
    return q


def parse_stoks_last_60(name):
    dic = {
        "GMKN": "https://ru.investing.com/equities/gmk-noril-nickel_rts-historical-data",
        "GAZP": "https://ru.investing.com/equities/gazprom_rts-historical-data",
        "SBER": "https://ru.investing.com/equities/sberbank_rts-historical-data",
        "AFLT": "https://ru.investing.com/equities/aeroflot-historical-data",
        "AAPL": "https://ru.investing.com/equities/apple-computer-inc-historical-data",
        "VTBR": "https://ru.investing.com/equities/vtb_rts-historical-data",
        "BA": "https://ru.investing.com/equities/boeing-co-historical-data",
        "INTC": "https://ru.investing.com/equities/intel-corp-historical-data",
        "MSFT": "https://ru.investing.com/equities/microsoft-corp-historical-data",
        "JPM": "https://ru.investing.com/equities/jp-morgan-chase-historical-data",
        "GS": "https://ru.investing.com/equities/goldman-sachs-group-historical-data",
        "KO": "https://ru.investing.com/equities/coca-cola-co-historical-data",
        "MCD": "https://ru.investing.com/equities/mcdonalds-historical-data",
        "AMZN": "https://ru.investing.com/equities/amazon-com-inc-historical-data",
        "ADSGn": "https://ru.investing.com/equities/adidas-salomon-historical-data",
        "SIEGn": "https://ru.investing.com/equities/siemens-historical-data",
        "DBKGn": "https://ru.investing.com/equities/deutsche-bank-historical-data",
        "HNKG_p": "https://ru.investing.com/equities/henkel-hgaa-vz-historical-data",
        "BMWG": "https://ru.investing.com/equities/bay-mot-werke-historical-data",
    }

    r = requests.get(dic[name])
    df = pd.read_html(r.content)
    s = []
    for i in df[1]["Объём"]:
        i = str(i)
        if i[-1] == "M":
            s.append(float(i[:-1].replace(",", ".")) * 10**6)
        elif i[-1] == "K":
            s.append(float(i[:-1].replace(",", ".")) * 10**3)
        elif i[-1] == "B":
            s.append(float(i[:-1].replace(",", ".")) * 10**9)
        else:
            s.append(float(i.replace(",", ".")))
    df[1].Объём = s
    df[1].columns = "date,last,open,max,min,volume,delta".split(",")
    df2 = (
        pd.read_csv("static/csv/" + name + ".csv")[::-1]
        .reset_index()
        .drop("index", axis=1)
    )
    s = [i.split(".")[::-1] for i in df2.date]
    ind = bisect(s, list(df[1].date)[-1].split(".")[::-1])
    k = 60 - len(df[1].volume)
    ans = []
    ans1 = []
    ans2 = []
    for i in range(ind - k, ind):
        ans1.append(df2["last"].values[i])
    for i in range(ind - k, ind):
        ans2.append(list(df2.volume)[i])
    ans = obr(list(ans1[::-1]) + list(df[1]["last"])) + obr(
        list(ans2[::-1]) + list(df[1]["volume"])
    )
    return list(df[1]["last"])[-1], ans


def get_cb():
    url = "https://cbr.ru/hd_base/KeyRate/"
    soup = BeautifulSoup(
        requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
        ).content,
        "html.parser",
    )
    table = soup.find("div", {"class": "table"})
    s = table.findAll("tr")[2:]
    q = s[-1].findAll("td")
    cost = float(q[1].text.replace(",", "."))
    return cost


def predict_money(want_date, name):
    url = "https://www.cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.so=1&UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.VAL_NM_RQ=R0{}&UniDbQuery.From={}&UniDbQuery.To={}"
    dic = {
        "GBP": 1035,  # Фунт стерлингов Соединенного королевства
        "USD": 1235,  # Доллар США
        "EUR": 1239,  # Евро
        "CNY": 1375,  # Юань
    }
    end = datetime.now().date()
    start = datetime.now().date() - timedelta(days=300)

    days = str(start.day)
    months = str(start.month)
    years = str(start.year)
    if len(days) == 1:
        days = "0" + days
    if len(months) == 1:
        months = "0" + months
    start = days + "." + months + "." + years
    days = str(end.day)
    months = str(end.month)
    years = str(end.year)
    if len(days) == 1:
        days = "0" + days
    if len(months) == 1:
        months = "0" + months
    end = days + "." + months + "." + years
    r = requests.get(
        url.format(dic[name], start, end),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    )
    soup = BeautifulSoup(r.content, "html.parser")
    table = soup.find("div", {"class": "table"})
    s = table.findAll("tr")[2:]
    costs = []
    for i in s:
        q = i.findAll("td")
        count = int(q[1].text)
        cost = float(q[2].text.replace(",", ".")) / count
        costs.append(cost)
    s = costs[:30][::-1]
    delta = (
        date(*reversed(list(map(int, want_date.split("."))))) - datetime.now().date()
    )
    delta = delta.days
    for i in range(delta):
        s.append(model.predict([s])[0])
        print(s[-1])
        s.pop(0)
    return s[-1]


@app.route("/")
@app.route("/index")
def index():  # Страница с графиками
    tablo = []
    buy = []
    sale = []
    stocks = [
        "GAZP",
        "SBER",
        "AFLT",
        "AAPL",
        "VTBR",
        "BA",
        "INTC",
        "MSFT",
        "JPM",
        "GS",
        "KO",
        "MCD",
        "AMZN",
        "ADSGn",
        "SIEGn",
        "DBKGn",
        "HNKG_p",
        "BMWG",
        "USD",
        "GBP",
        "EUR",
        "CNY",
    ]
    try:
        with open("static/csv/tablo.csv", "r") as f:  # Формирую данные для табло
            reader = csv.reader(f)
            for row in reader:
                tablo.append(row)

        with open("static/csv/buy.csv", "r") as f:  # Формирую данные для покупки
            reader = csv.reader(f)
            for row in reader:
                buy.append(row)

        with open("static/csv/sale.csv", "r") as f:  # Формирую данные для продажи
            reader = csv.reader(f)
            for row in reader:
                sale.append(row)

        tablo = tablo[1:]
        buy = buy[1:]
        sale = sale[1:]

        for i, e in enumerate(buy):
            buy[i] = [e[0], e[1], str(round(float(e[2]), 2))]

        for i, e in enumerate(sale):
            sale[i] = [e[0], e[1], str(round(float(e[2]), 2))]

    except Exception as ex:
        print(ex)

    return render_template(
        "index.html",
        tablo=tablo,
        buy=buy,
        sale=sale,
        fon=get_fon(),
        stocks=stocks,
        get_price=get_price,
        parse_money=parse_money,
        parse_stoks=parse_stoks,
        couple_money=couple_money,
        cb=get_cb(),
    )


@app.route("/submitted", methods=["POST"])
def submitted():
    date = ".".join(request.form.get("date").split("-")[::-1])
    name = request.form.get("name")
    return render_template("course.html", course=get_price(date, name))


def create_HHTP_tablet(name):  # Функция подготавливающая данные для HTML графика
    d100 = pd.read_csv("static/csv/d100.csv")
    data = []
    diff = []
    last = 0
    for i, e in enumerate(d100[name]):
        if i == 0:
            diff.append([i, 0])
        else:
            diff.append([i, e - last])
        data.append([i, e])
        last = e
    return data, diff


@app.route("/ticket/<name>")
def ticket(name):  # Главная страница
    data, diff = create_HHTP_tablet(name)  # Подготовка данных для HTTP графика
    create_plots.save_plot_by_name(name)  # Создание графика цен
    create_plots.save_predict_by_name(name)  # Создание графика предсказанных цен

    return render_template("ticket.html", name=name, data=data, diff=diff)


def goodbye():
    path = "static/Pictures/temp"

    f = os.listdir(path)
    for i in f:
        os.remove(path + "/" + i)  # Удаление графиков


atexit.register(goodbye)  # Перехват выхода из приложения


if __name__ == "__main__":
    # import parser
    import recommendation

    app.run(port=8080, host="0.0.0.0")
