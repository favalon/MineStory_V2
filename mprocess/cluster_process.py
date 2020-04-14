import os
import numpy as np
from general import tools
from general.cluster import Cluster, ChooseCluster
from general.save_load import SaveBasic


def select_movies_plot(movies_plot_pool, c_role):
    movies_plot = {}
    for p_id in movies_plot_pool.keys():
        if c_role in movies_plot_pool[p_id].char_role_dict.keys():
            movies_plot[p_id] = movies_plot_pool[p_id]
    return movies_plot


def process(movies_plot_pool, c_role, fp=None, n_clusters=None, save=False):
    if not os.path.isdir(fp) and save:
        print("cluster_process save path wrong")
        return

    statuses_cluster = {}
    if n_clusters is not None:
        selected_statues = [0, 1, 2, 3, 4]
        for j, status in enumerate(selected_statues):
            movies_plot = select_movies_plot(movies_plot_pool, c_role)
            status_cluster, edc_dis = ChooseCluster.cluster_status(movies_plot, c_role, status,
                                                                   n_clusters=n_clusters[j], cluster='k-mean')

            statuses_cluster[status] = status_cluster

    return statuses_cluster


