import pandas as pd
from flask import Flask, request, render_template, redirect
from pyecharts.charts import Bar, Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

df = pd.read_excel('kafka.xlsx')
print(df)
# print(df[["每条消息大小（B）", "消息发送速率（条/s）", "平均时延（ms）", "最大时延（ms）", "50%消息时延（ms）", "95%消息时延（ms）",
#           "99%消息时延（ms）", "99.9%消息时延（ms）", "平均吞吐量（MB/s）"]])
# p = df.loc[0, "producer数量"]
# c = df.loc[0, "consumer数量"]
# t = df.loc[0, "producer写入topic数量"]

# 根据 A、B 列的值将数据分组
grouped = df.groupby(
    ['producer数量', 'consumer数量', 'producer写入topic数量', '磁盘类型', 'socket.send.buffer.bytes（B）'])

p_set = set(df['producer数量'])
c_set = set(df['consumer数量'])
t_set = set(df['producer写入topic数量'])
d_set = set(df['磁盘类型'])
b_set = set(df['socket.send.buffer.bytes（B）'])


# 定义函数将每个组的 C 列数据存放到对应的列表中
def add_to_list(group):
    category = f"{group['producer数量'].iloc[0]}-{group['consumer数量'].iloc[0]}-{group['producer写入topic数量'].iloc[0]}-{group['磁盘类型'].iloc[0]}-{group['socket.send.buffer.bytes（B）'].iloc[0]}"
    categories.setdefault(category, []).extend(group['消息发送速率（条/s）'].tolist())


# 对每个组应用函数
categories = {}
grouped.apply(add_to_list)

app = Flask(__name__, static_folder="templates")

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))


def line_base():
    x_data = [str(i) for i in df["每条消息大小（B）"]]
    line = Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
    line.add_xaxis(x_data)
    for y_name in categories:
        line.add_yaxis(y_name, categories[y_name])
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="消息条数吞吐量"),
        xaxis_opts=opts.AxisOpts(type_="value", name="每条消息大小（B）"),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="消息发送速率（条/s）",
        )
    )
    return line


@app.route("/",methods=["GET"])
def index():
    if request.method == "GET":
        return render_template('index.html', producers=p_set, consumers=c_set, topics=t_set, disks=d_set, buffers=b_set)


@app.route("/find")
def find():
    x_data = [str(i) for i in df["每条消息大小（B）"]]
    line = Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
    line.add_xaxis(x_data)
    args = request.args
    template = [-1 for _ in range(4)]
    template[0] = args.get("producer", -1)
    template[1] = args.get("consumer", -1)
    template[2] = args.get("topic", -1)
    template[3] = args.get("disk", -1)
    template[4] = args.get("buffer", -1)
    for y_name in categories:
        y_n = y_name.split("-")[0:4]
        if template[0] == y_n[0]:
            line.add_yaxis(y_name, categories[y_name])
        elif template[1] == y_n[1]:
            line.add_yaxis(y_name, categories[y_name])
        elif template[2] == y_n[2]:
            line.add_yaxis(y_name, categories[y_name])
        elif template[3] == y_n[3]:
            line.add_yaxis(y_name, categories[y_name])
    line.set_global_opts(
        title_opts=opts.TitleOpts(title="消息条数吞吐量"),
        xaxis_opts=opts.AxisOpts(type_="value", name="每条消息大小（B）"),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            name="消息发送速率（条/s）",
        )
    )
    return Markup(line.render_embed())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=35000)
