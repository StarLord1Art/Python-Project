import os
import glob

data = []
import pandas as pd


for name in glob.glob("static\\csv\\test\\*.csv"):
    name = name.split("\\")[-1]
    print("static\\csv\\test\\" + name)
    with open("static\\csv\\test\\" + name, "r") as f:
        d = f.read().replace('","', ";").replace('"', "")
    with open("static\\csv\\test\\" + name, "w") as f:
        f.write(d)

print("----------------------------")

col = ["date", "last", "open", "max", "min", "volume", "delta"]
for name in glob.glob("static\\csv\\test\\*.csv"):
    print(name)
    name = name.split("\\")[-1]
    df = pd.read_csv("static\\csv\\test\\" + name, sep=";")
    df.columns = col

    s = []
    for i in df["volume"]:
        i = str(i)
        if i[-1] == "M":
            s.append(float(i[:-1].replace(",", ".")) * 10**6)
        elif i[-1] == "K":
            s.append(float(i[:-1].replace(",", ".")) * 10**3)
        elif i[-1] == "B":
            s.append(float(i[:-1].replace(",", ".")) * 10**9)
        else:
            s.append(float(i.replace(",", ".")))
    df.volume = s

    s = []
    for i in df["delta"]:
        s.append(float(i[:-1].replace(",", ".")) / 100)
    df["delta"] = s

    for j in ["last", "open", "max", "min"]:
        s = []
        for i in df[j]:
            try:
                s.append(float(i.replace(",", ".")))
            except:
                s.append(float(i.replace(".", "").replace(",", ".")))
        df[j] = s

        df.to_csv("static\\csv\\stoks\\" + name, index=False)
