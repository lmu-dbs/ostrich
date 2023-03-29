import os

import matplotlib.pyplot as plt
import numpy as np
from pyclustering.cluster import cluster_visualizer_multidim
from pyclustering.cluster.optics import optics, ordering_analyser, ordering_visualizer
from sklearn.cluster import OPTICS

from constants import CLUSTER_THRESHOLD


class SubCluster:

    def __init__(self, path):
        self.path = path
        self.clusters = []

    def run(self, ignore_singles=False):
        self.read_files_single(ignore_singles)

    def read_files(self):
        for file in os.listdir(self.path):
            durations = []
            print("\n FILE \n")
            with open(os.path.join(self.path, file), "r") as f:
                content = f.readlines()
                for line in content[1:]:
                    line = [int(i) for i in line.split(" ")]  # cast each element in list to int
                    d = np.diff(line)
                    durations.append(d)
            print(durations)
            self.cluster(durations)

    def read_files_single(self, ignore_singles):
        time_vectors = []
        cids = []
        rule = None
        t = []
        with open(os.path.join(self.path, "projections.txt"), "r") as f:
            content = f.readlines()
            for line in content:
                if line.startswith("#"):

                    if rule is None:
                        time_vectors = []
                        cids = []
                        rule = line.split("] ==> [")
                        ant = rule[0][8:]
                        cons = rule[1][:-2]
                        ant_l = [int(x) for x in ant.split(",")]  # List of the elements in ants
                        cons_l = [int(x) for x in cons.split(",")]
                        # print(ant_l, cons_l)

                        # DEBUGGING ###
                        # Rules with just 1 el on left and right side get ignored
                        if ignore_singles and len(ant_l) == 1 and len(cons_l) == 1:
                            rule = None
                            time_vectors = []
                            cids = []
                            continue

                    else:
                        #self.cluster_2(time_vectors, cids, rule)  # TODO: change clustering version for OPTICS here
                        self.cluster(time_vectors, cids, rule)
                        rule = line.split("] ==> [")

                        time_vectors = []
                        cids = []
                else:
                    line = line.split(": ")
                    cid = int(line[0])
                    temp = [int(x) for x in line[1].split(",")]
                    # first coordinate obsolete
                    temp_left_aligned = [temp[1] - temp[0], temp[2] - temp[0], temp[3] - temp[0]]
                    time_vectors.append(temp_left_aligned)
                    cids.append(cid)


    def cluster(self, time_vectors, cids, rule):
        # Used pyclustering package
        # Inspired by https://analyticsindiamag.com/a-guide-to-clustering-with-optics-using-pyclustering/
        print(time_vectors)
        print(f"Rule: {rule}")

        ant = rule[0].split("[")[1].replace(" ", "")
        cons = rule[1].split("]")[0].replace(" ", "")
        r = ant + "-" + cons
        rule_title = "Rule: " + ant + " ==> " + cons
        print(f"Rule {rule_title}")

        eps = MAX_EPS
        minpts = MIN_SAMPLES
        optics_model = optics(time_vectors, eps, minpts)

        optics_model.process()

        clusters = optics_model.get_clusters()
        noise = optics_model.get_noise()
        ordering = optics_model.get_ordering()
        analyser_cluster = ordering_analyser(ordering)

        plot = ordering_visualizer().show_ordering_diagram(analyser_cluster)
        plots = cluster_visualizer_multidim()
        plots.append_clusters(clusters, time_vectors)

        plots.show()



    def cluster_2(self, time_vectors, cids, rule):

        ant = rule[0].split("[")[1].replace(" ", "")
        cons = rule[1].split("]")[0].replace(" ", "")
        r = ant + "-" + cons
        rule_title = "Rule: " + ant + " ==> " + cons
        print(f"Rule {rule_title}")

        clust = OPTICS(min_samples=MIN_SAMPLES, max_eps=MAX_EPS, xi=0.05, metric='euclidean')  # 1''' ms = 11,57 Tage

        # Run the fit
        clust.fit(time_vectors)

        space = np.arange(len(time_vectors))
        reachability = clust.reachability_[clust.ordering_]
        adjusted_reachability = []
        for el in reachability:
            if el == np.inf:
                el = MAX_EPS + 100000
            adjusted_reachability.append(el)

        labels = clust.labels_[clust.ordering_]

        plt.figure(figsize=(28, 5))

        # Reachability plot
        colors = ["g", "g", "g", "r", "b", "b", "b", "y", "c", "m", "fuchsia",
                  "firebrick", "yellow", "silver", "blueviolet"]

        # Labels of cases on x-axis
        x_cID = [None] * len(clust.ordering_)
        for i in range(0, len(clust.ordering_)):
            x_cID[i] = cids[clust.ordering_[i]]

        reach_list = list(reachability)
        clusters = []
        cluster = []
        for i, cid in enumerate(x_cID):
            if reach_list[i] < CLUSTER_THRESHOLD:
                cluster.append(cid)
            elif reach_list[i] >= CLUSTER_THRESHOLD and len(cluster) > 0:
                clusters.append(cluster)
                cluster = []

        adjusted_reachability = np.array(adjusted_reachability)

        j = 0
        for klass in range(0, len(colors)):
            Xk_ticks = space[labels == klass]
            Rk = adjusted_reachability[labels == klass]
            plt.plot(Xk_ticks, Rk, colors[j], marker="o", linestyle="None", alpha=1, markersize=3)
            j += 1
        plt.xticks(range(len(cids)), x_cID, rotation=90, fontsize=8)
        plt.plot(space[labels == -1], adjusted_reachability[labels == -1], "k.", alpha=0.5, markersize=6)
        plt.xlabel("CaseIDs ordered according to OPTICS")
        plt.ylabel("Reachability (epsilon distance) (euclidian)")
        plt.title("Reachability Plot " + str(rule_title))

        plt.savefig(os.path.join(".", self.path, str(r + ".svg")))
        plt.close()



if __name__ == "__main__":
    path = os.path.join("results", "2023-03-08_13-45-32")
    MIN_SAMPLES = 250
    MAX_EPS = 10000000
    clusterer = SubCluster(path)
    clusterer.run(ignore_singles=False)
