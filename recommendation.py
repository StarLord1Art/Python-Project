# -*- coding: utf-8 -*-

import seaborn as sns
import pandas as pd
import warnings

warnings.filterwarnings("ignore")


columns = ["name", "last_price", "feature"]

to_buy = pd.DataFrame(columns=columns)  # создаю датафрейм для покупок
to_sale = pd.DataFrame(columns=columns)  # создаю датафрейм для продажи


d100 = pd.read_csv("static/csv/d100.csv")
tablo = pd.read_csv("static/csv/tablo.csv")


import pickle

with open("model.pkl", "rb") as file:  # Загрузка модели
    model = pickle.load(file)

for i in d100:  # Формирование спика рекомендаций к покупке
    now = model.predict([d100[i][-30:]])[0]
    to_buy.loc[to_buy.shape[0]] = [
        i,
        float(tablo.loc[tablo.name == i]["last"]),
        (now - float(tablo.loc[tablo.name == i]["last"]))
        / float(tablo.loc[tablo.name == i]["last"])
        * 100,
    ]

for i in d100:  # Формирование спика рекомендаций к продаже
    now = model.predict([d100[i][-30:]])[0]
    to_sale.loc[to_sale.shape[0]] = [
        i,
        float(tablo.loc[tablo.name == i]["last"]),
        (now - float(tablo.loc[tablo.name == i]["last"]))
        / float(tablo.loc[tablo.name == i]["last"])
        * -100,
    ]

to_buy.sort_values(by="feature", ascending=False).head().to_csv(
    "static/csv/buy.csv", index=False
)

to_sale.sort_values(by="feature", ascending=False).head().to_csv(
    "static/csv/sale.csv", index=False
)
