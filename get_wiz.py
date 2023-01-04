import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from collections import defaultdict

from typing import Dict

plt.rcParams["text.usetex"] = True
plt.rcParams["text.latex.preamble"] = "\\usepackage{polski}"
plt.rcParams["figure.figsize"] = (8,4)
plt.rcParams["figure.autolayout"] = False
plt.rcParams["savefig.pad_inches"] = 0.01
plt.rcParams["axes.axisbelow"] = True
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Helvetica"

out: Dict[int, dict] = {}
graph: Dict[int, nx.DiGraph] = {}

def get_table(data: list) -> str:
    ret = ""
    rows = len(data)
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


for year in range(2006, 2024):
    with open(f"out/{year}.json") as file:
        out[year] = json.load(file)
    graph[year] = nx.DiGraph()
    for key, links in out[year].items():
        for link in links:
            graph[year].add_edge(key, link)
    

size = []
conns = []

for year in range(2006, 2024):
    size.append(len(out[year]))
    conns.append(sum([len(i) for i in out[year].values()]))

#
# size
#

fig, ax = plt.subplots()
l1 = ax.plot(size, label="Ilość artykułów")
ax.set_xticklabels(range(2006, 2024, 2))
ax.set_xticks(range(0, 2024-2006, 2))
ax.grid()
ax.set_xlabel("Rok [1]")
ax.set_ylabel("Ilość artykułów [1]")

ax1 = ax.twinx()
l2 = ax1.plot(conns, color="green", label="Ilość połączeń")
ax1.set_ylabel("Ilość połączeń [1]")

lns = l1+l2
labs = [l.get_label() for l in lns]
ax.legend(lns, labs, loc=0)

fig.savefig("sprawko/figures/size.pdf", bbox_inches="tight")

#
# density
#

density = []

for year in range(2006, 2024):
    density.append(nx.density(graph[year]))

fig, ax = plt.subplots()
ax.plot(density)
ax.set_xticklabels(range(2006, 2024, 2))
ax.set_xticks(range(0, 2024-2006, 2))
ax.grid()
ax.set_xlabel("Rok [1]")
ax.set_ylabel("Gęstość [1]")

fig.savefig("sprawko/figures/density.pdf", bbox_inches="tight")

#
# mean shortest path length
#

weak: Dict[int, nx.Graph] = {}
weak_connected_size = []


for year in range(2006, 2024):
    single = []
    for i in reversed(list(nx.weakly_connected_components(graph[year]))):
        single.append(len(i))
    weak_connected_size.append(single)
    weak[year] = graph[year].subgraph(i).to_undirected()

# its long, >45 mins on 3600X
# for year in range(2006, 2024):
#     print(year)
#     mean_shortest_path.append(nx.average_shortest_path_length(weak[year]))
# thats the answer 
mean_shortest_path = [4.535974785676563, 4.559513853790594, 4.537310943036935, 4.5125297364174335, 4.50142968987336, 4.483276943285383, 4.471417590900967, 4.4398312877425505, 4.443271923116117, 4.458404691672049, 4.452706683493887, 4.44553146853324, 4.341846945559295, 4.345599776223152, 4.337191808625235, 4.31852321555978, 4.319142761068016, 4.319000649000121]

fig, ax = plt.subplots()
ax.plot(mean_shortest_path)
ax.set_xticklabels(range(2006, 2024, 2))
ax.set_xticks(range(0, 2024-2006, 2))
ax.grid()
ax.set_xlabel("Rok [1]")
ax.set_ylabel("Średnia długość ścieżki [1]")

fig.savefig("sprawko/figures/path.pdf", bbox_inches="tight")

fig, ax = plt.subplots()
for year in range(2006, 2024):
    ax.hist([x[1] for x in nx.degree(graph[year])], bins=25)

fig.savefig("sprawko/figures/degreehist.pdf", bbox_inches="tight")

# ax[0].hist(_3, label="2023", bins=50, range=(1, 51), alpha=0.95, zorder=1)

fig, ax = plt.subplots()
for year in [2023, 2018, 2013, 2008]:
    data = np.array([x[1] for x in nx.degree(graph[year])])
    hist, _ = np.histogram(data, bins=50, range=(1, 51))
    ax.bar(np.arange(1, 51), hist, width=1, bottom=np.zeros_like(hist), label=f"{year}", alpha=0.90, zorder=1)
ax.set_xlabel("Stopień wierzchołka [1]")
ax.set_ylabel("Ilośc wierzchołków [1]")
ax.set_yscale("log")
ax.legend()
ax.grid()

fig.savefig("sprawko/figures/degreehist.pdf", bbox_inches="tight")

_max = []
_mean = []
_word = []
year_range = list(range(2008, 2024, 3))
for year in year_range:
    degrees = nx.degree(graph[year])
    word, deg_max = max(degrees, key=lambda a: a[1])
    _word.append(word)
    _max.append(deg_max)
    _mean.append(f"{np.round(np.array([x[1] for x in degrees]).mean(), 3):.05}")

table = []
table += [["Rok", *year_range]]
table += [["Max", *_max]]
table += [["Średnia", *_mean]]
table += [["Artykuł", *_word]]

save_table("sprawko/data/maxmean.tex", np.array(table).T)

joint = []
amount = []

for year in year_range:
    print(year)
    ret = defaultdict(int)
    for source, targets in dict(nx.all_pairs_shortest_path(graph[year])).items():
        for target, path in targets.items():
            if source == target:
                continue
            for node in path:
                ret[node] += 1
    _joint, _amount = max(list(ret.items()), key=lambda a: a[1])
    joint.append(_joint)
    amount.append(_amount)

table = []
table += [["Rok", *year_range]]
table += [["Artykuł", *joint]]
table += [["Ścieżki", *amount]]

save_table("sprawko/data/joints.tex", np.array(table).T)