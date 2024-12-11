import pickle
import matplotlib.pyplot as plt
import pandas as pd


class Model:
    def __init__(self):
        pass

    def predict(self, *args):
        return [1.5]


with open("model.pkl", "rb") as file:  # Закрузка модели
    model = pickle.load(file)

d100 = pd.read_csv("static/csv/d100.csv")


def save_plot_by_name(name):  # Создание графика цен
    fig = plt.figure(figsize=(12, 5))
    plt.plot([i for i in range(len(d100[name]))], d100[name])
    plt.fill_between([i for i in range(len(d100[name]))], d100[name])
    plt.legend()
    plt.title(name)
    plt.savefig(f"static/Pictures/temp/{name}.png")


def predict(col, k):  # предсказание акции name моделью model на k дней
    col = col.to_list()
    ans = col[:]
    for i in range(k):
        q = model.predict([col])[0]
        col.append(q)
        ans.append(q)
        col.pop(0)
    return ans


def save_predict_by_name(name):  # Создание графика предсказанных цен
    fig = plt.figure(figsize=(12, 5))
    plt.plot(
        [i for i in range(len(d100[name]))],
        d100[name][10:70].to_list() + predict(d100[name][70:], 10),
    )
    plt.fill_between([i for i in range(90)], d100[name][10:].to_list())
    plt.fill_between(
        [i for i in range(89, 100)], predict(d100[name][70:], 10)[-11:], color="red"
    )
    plt.legend()
    plt.title(name)
    plt.savefig(f"static/Pictures/temp/{name}1.png")
