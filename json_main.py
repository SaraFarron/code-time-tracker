import json
from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_data(path):
    with open(path, "r", encoding="utf-8") as file:
        json_data = json.load(file)["days"]
    return json_data


def get_value(data, *keys):
    for key in keys:
        data = data[key]
    return data


def populate_table(items: list, pull: dict, date: str, *path):
    for item in items:
        name = item["name"]
        if name not in pull:
            pull[name] = {}
        seconds = get_value(item, *path)
        pull[name][date] = round(seconds / 3600, 2)


def append_day_time(date: str, days: dict, total_seconds: float):
    days["time"].append(datetime.strptime(date, "%Y-%m-%d"))
    days["total_minutes"].append(round(total_seconds / 3600, 2))


def import_data():
    projects, op_sys, langs, devices = {}, {}, {}, {}
    days = {"time": [], "total_minutes": []}
    for day in get_data("data.json"):
        date = day["date"]
        append_day_time(date, days, day["grand_total"]["total_seconds"])
        prjcts = day.get("projects", {})
        if prjcts:
            populate_table(prjcts, projects, date,
                           "grand_total", "total_seconds")
        opers = day.get("operating_systems", {})
        if opers:
            populate_table(opers, op_sys, date, "total_seconds")
        languages = day.get("languages", {})
        if languages:
            populate_table(languages, langs, date, "total_seconds")
        machines = day.get("machines", {})
        if machines:
            populate_table(machines, devices, date, "total_seconds")
    return projects, op_sys, langs, days, devices


def create_cumulative_data(data: list):
    res_x, res_y = [], []
    for date, hours in data.items():
        res_x.append(datetime.strptime(date, "%Y-%m-%d"))
        if not res_y:
            res_y.append(hours)
            continue
        res_y.append(hours + res_y[-1])
    return res_x, res_y


def create_bar(data: dict):
    fig = make_subplots(1, 1)
    fig.add_bar(
        x=data["time"], y=data["total_minutes"], name="activity",
        row=1, col=1
    )
    fig.update_layout(title_text="Bars", template="plotly_dark")
    fig.show()


def create_plot(data: dict):
    fig = make_subplots(1, 1)
    for name, value in data.items():
        fig.add_trace(
            go.Line(x=value["time"], y=value["hours"], name=name),
            row=1,
            col=1
        )
    fig.update_layout(title_text="Plots", )
    fig.show()


def main():
    projects, opers, languages, days, devices = import_data()

    for dataset in projects, opers, languages, devices:
        for dataname, datavalue in dataset.items():
            x_value, y_value = create_cumulative_data(datavalue)
            dataset[dataname] = {"time": x_value, "hours": y_value}

    # create_plot(projects)
    # create_plot(opers)
    # create_plot(languages)
    create_plot(devices)
    # create_bar(days)


if __name__ == "__main__":
    main()
