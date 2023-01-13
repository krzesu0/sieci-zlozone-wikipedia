import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from collections import defaultdict

from typing import Dict, List

plt.rcParams["text.usetex"] = True
plt.rcParams["text.latex.preamble"] = "\\usepackage{polski}"
plt.rcParams["figure.figsize"] = (8,4)
plt.rcParams["figure.autolayout"] = False
plt.rcParams["savefig.pad_inches"] = 0.01
plt.rcParams["axes.axisbelow"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Helvetica"


def get_table(data: list) -> str:
    ret = ""
    columns = len(data[0])
    ret += f"""\\begin{{tabular}}{{|{"|".join(['c']*columns)}|}}
\t\\hline
"""
    for row in data:
        ret += "\t"
        ret += " &\t".join([str(i) for i in row])
        ret += " \\nl\n"

    ret += """\\end{tabular}"""
    return ret

def save_table(filename: str, data: list):
    with open(filename, "w") as file:
        file.write(get_table(data))

# save_table("sprawko/data/test.tex", [[1, 2, 3], [3, 2, 1], ["a", "b", "c"]])
# exit(-1)

year_range = list(range(2008, 2024, 3))


def load_data(name: str):
    out: Dict[int, dict] = {}
    graph: Dict[int, nx.DiGraph] = {}
    weak: Dict[int, nx.Graph] = {}
    weak_sizes: List[int] = []

    for year in range(2006, 2024):
        with open(f"{name}/{year}.json") as file:
            out[year] = json.load(file)
        graph[year] = nx.DiGraph()
        for key, links in out[year].items():
            for link in links:
                graph[year].add_edge(key, link)
        single = []
        for i in reversed(list(nx.weakly_connected_components(graph[year]))):
            single.append(len(i))
        weak_sizes.append(single)
        weak[year] = graph[year].subgraph(i).to_undirected()
        
    return out, graph, weak, weak_sizes


def get_sizes(data: Dict[int, dict]):
    size, conns = [], []
    for year in range(2006, 2024):
        size.append(len(data[year]))
        conns.append(sum([len(i) for i in data[year].values()]))
    return size, conns

def get_density(data: Dict[int, dict]):
    density = []
    for year in range(2006, 2024):
        density.append(nx.density(data[year]))
    return density

def get_max_mean_word(data):
    _max = []
    _mean = []
    _word = []
    for year in year_range:
        degrees = nx.degree(data[year])
        word, deg_max = max(degrees, key=lambda a: a[1])
        _word.append(word)
        _max.append(deg_max)
        _mean.append(f"{np.round(np.array([x[1] for x in degrees]).mean(), 3):.05}")
    return _max, _mean, _word

def get_join_amount(data):
    joint = []
    amount = []
    n = 0
    for year in year_range:
        print(year)
        ret = defaultdict(int)
        for source, targets in dict(nx.all_pairs_shortest_path(data[year])).items():
            for target, path in targets.items():
                if source == target:
                    continue
                for node in path:
                    ret[node] += 1
                    n += 1
        _joint, _amount = max(list(ret.items()), key=lambda a: a[1])
        joint.append(_joint)
        amount.append(np.round(_amount / n * 100, 2))
    return joint, amount

out_pl, graph_pl, weak_pl, weak_sizes_pl = load_data("out_pl")
out_en, graph_en, weak_en, weak_sizes_en = load_data("out_en")

size_pl, conns_pl = get_sizes(out_pl)
size_en, conns_en = get_sizes(out_en)

max_pl, mean_pl, word_pl = get_max_mean_word(graph_pl)
max_en, mean_en, word_en = get_max_mean_word(graph_en)

joint_pl, amount_pl = get_join_amount(graph_pl)
joint_en, amount_en = get_join_amount(graph_en)

density_pl = get_density(graph_pl)
density_en = get_density(graph_en)

mean_shortest_path_pl = [4.535974785676563, 4.559513853790594, 4.537310943036935, 4.5125297364174335, 4.50142968987336, 4.483276943285383, 4.471417590900967, 4.4398312877425505, 4.443271923116117, 4.458404691672049, 4.452706683493887, 4.44553146853324, 4.341846945559295, 4.345599776223152, 4.337191808625235, 4.31852321555978, 4.319142761068016, 4.319000649000121]
mean_shortest_path_en = [4.648619922092376, 4.903445026895536, 4.865338400140719, 4.9084923508201665, 4.833372902123132, 4.60084588806798, 4.590124586760466, 4.588517388067128, 4.6175243492434115, 4.6381889096794255, 4.612590582903891, 4.554748566010606, 4.519510593657234, 4.498348431128938, 4.447135633052009, 4.408498214796173, 4.3931454874040545, 4.369543046991977]

# its long, >45 mins on 3600X for PL
# >4.5hrs on i3-3225 for EN
# for year in range(2006, 2024):
#     print(year)
#     mean_shortest_path.append(nx.average_shortest_path_length(weak[year]))
# # thats the answer
# print(mean_shortest_path)


fig, ax = plt.subplots()
l1 = ax.plot(size_pl, label="Ilość artykułów")
ax.set_xticklabels(range(2006, 2024, 2))
ax.set_xticks(range(0, 2024-2006, 2))
ax.grid()
ax.set_xlabel("Rok [1]")
ax.set_ylabel("Ilość artykułów [1]")

ax1 = ax.twinx()
l2 = ax1.plot(conns_pl, color="green", label="Ilość połączeń")

lns = l1+l2
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)
ax1.set_ylabel("Ilość połączeń [1]")

fig.savefig("sprawko/figures/size_pl.pdf", bbox_inches="tight")


fig, ax = plt.subplots()
ax.plot(density_pl)
ax.set_xticklabels(range(2006, 2024, 2))
ax.set_xticks(range(0, 2024-2006, 2))
ax.grid()
ax.set_xlabel("Rok [1]")
ax.set_ylabel("Gęstość [1]")

fig.savefig("sprawko/figures/density_pl.pdf", bbox_inches="tight")


fig, ax = plt.subplots()
ax.plot(mean_shortest_path_pl)
ax.set_xticklabels(range(2006, 2024, 2))
ax.set_xticks(range(0, 2024-2006, 2))
ax.grid()
ax.set_xlabel("Rok [1]")
ax.set_ylabel("Średnia długość ścieżki [1]")

fig.savefig("sprawko/figures/path_pl.pdf", bbox_inches="tight")


fig, ax = plt.subplots()
for year in [2023, 2018, 2013, 2008]:
    data = np.array([x[1] for x in nx.degree(graph_pl[year])])
    hist, _ = np.histogram(data, bins=50, range=(1, 51))
    ax.bar(np.arange(1, 51), hist, width=1, bottom=np.zeros_like(hist), label=f"{year}", alpha=0.90, zorder=1)
ax.set_xlabel("Stopień wierzchołka [1]")
ax.set_ylabel("Ilośc wierzchołków [1]")
ax.set_yscale("log")
ax.legend()
ax.grid()

fig.savefig("sprawko/figures/degreehist_pl.pdf", bbox_inches="tight")


table = []
table += [["Rok", *year_range]]
table += [["Max", *max_pl]]
table += [["Średnia", *mean_pl]]
table += [["Artykuł", *word_pl]]

save_table("sprawko/data/maxmean_pl.tex", np.array(table).T)


table = []
table += [["Rok", *year_range]]
table += [["Artykuł", *joint_pl]]
table += [["Ścieżki", *amount_pl]]

save_table("sprawko/data/joints_pl.tex", np.array(table).T)

### ENG ###

fig, ax = plt.subplots(1, 2, sharey=True)
l1 = ax[0].plot(size_pl, label="Ilość artykułów")
ax[0].set_xticklabels(range(2006, 2024, 4))
ax[0].set_xticks(range(0, 2024-2006, 4))
ax[0].set_xlabel("Rok [1]")
ax[0].set_ylabel("Ilość artykułów [1]")
ax[0].set_title("Informatyka")

ax1 = ax[0].twinx()
ax1.set_yticklabels([""] * len(ax1.get_yticklabels()))
ax[0].grid()
ax1.grid(c="#eaeaea")
l2 = ax1.plot(conns_en, color="green", label="Ilość połączeń")


lns = l1+l2
labs = [l.get_label() for l in lns]
ax[0].legend(lns, labs, loc=0)

ax[1].plot(size_en, label="Ilość artykułów")
ax[1].set_xticklabels(range(2006, 2024, 4))
ax[1].set_xticks(range(0, 2024-2006, 4))
ax[1].set_xlabel("Rok [1]")
ax[1].set_title("Information technology")

ax2 = ax[1].twinx()
ax2.get_shared_y_axes().join(ax1, ax2)
ax[1].grid()
ax2.grid(c="#eaeaea")
ax2.plot(conns_en, color="green", label="Ilość połączeń")
ax2.set_ylabel("Ilość połączeń [1]")

fig.savefig("sprawko/figures/size_en.pdf", bbox_inches="tight")


fig, ax = plt.subplots(1, 2, sharey=True)
ax[0].plot(density_pl)
ax[0].set_xticklabels(range(2006, 2024, 4))
ax[0].set_xticks(range(0, 2024-2006, 4))
ax[0].grid()
ax[0].set_xlabel("Rok [1]")
ax[0].set_ylabel("Gęstość [1]")
ax[0].set_title("Informatyka")

ax[1].plot(density_en)
ax[1].set_xticklabels(range(2006, 2024, 4))
ax[1].set_xticks(range(0, 2024-2006, 4))
ax[1].grid()
ax[1].set_xlabel("Rok [1]")
ax[1].set_title("Information technology")

fig.savefig("sprawko/figures/density_en.pdf", bbox_inches="tight")


fig, ax = plt.subplots(1, 2, sharey=True)
ax[0].plot(mean_shortest_path_pl)
ax[0].set_xticklabels(range(2006, 2024, 4))
ax[0].set_xticks(range(0, 2024-2006, 4))
ax[0].grid()
ax[0].set_xlabel("Rok [1]")
ax[0].set_ylabel("Średnia długość ścieżki [1]")
ax[0].set_title("Informatyka")

ax[1].plot(mean_shortest_path_en)
ax[1].set_xticklabels(range(2006, 2024, 4))
ax[1].set_xticks(range(0, 2024-2006, 4))
ax[1].grid()
ax[1].set_xlabel("Rok [1]")
ax[1].set_title("Information technology")

fig.savefig("sprawko/figures/path_en.pdf", bbox_inches="tight")


fig, ax = plt.subplots(1, 2, sharey=True)
for year in [2023, 2018, 2013, 2008]:
    data_pl = np.array([x[1] for x in nx.degree(graph_pl[year])])
    data_en = np.array([x[1] for x in nx.degree(graph_en[year])])
    hist_pl, _ = np.histogram(data_pl, bins=50, range=(1, 51))
    hist_en, _ = np.histogram(data_en, bins=50, range=(1, 51))
    ax[0].bar(np.arange(1, 51), hist_pl, width=1, bottom=np.zeros_like(hist), label=f"{year}", alpha=0.90, zorder=1)
    ax[1].bar(np.arange(1, 51), hist_en, width=1, bottom=np.zeros_like(hist), label=f"{year}", alpha=0.90, zorder=1)
ax[0].set_xlabel("Stopień wierzchołka [1]")
ax[0].set_ylabel("Ilośc wierzchołków [1]")
ax[0].set_yscale("log")
ax[0].set_title("Informatyka")
ax[0].legend()
ax[0].grid()

ax[1].set_xlabel("Stopień wierzchołka [1]")
ax[1].set_title("Information technology")
ax[1].grid()

fig.savefig("sprawko/figures/degreehist_en.pdf", bbox_inches="tight")


table = []
table += [["Rok", *year_range]]
table += [["Max", *max_en]]
table += [["Średnia", *mean_en]]
table += [["Artykuł", *word_en]]

save_table("sprawko/data/maxmean_en.tex", np.array(table).T)


table = []
table += [["Rok", *year_range]]
table += [["Artykuł", *joint_en]]
table += [["Ścieżki", *[f"{i}\%" for i in amount_en]]]

save_table("sprawko/data/joints_en.tex", np.array(table).T)
