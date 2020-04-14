import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from pathlib import Path


class ChooseCluster:
    @staticmethod
    def cluster_status(movies_plot, c_role, status, min_threshold=10, n_clusters=25, cluster='k-mean'):
        if cluster == 'k-mean':
            status_cluster, edc_dis = ChooseCluster.\
                cluster_k_mean(movies_plot, c_role, status, min_threshold=min_threshold, n_clusters=n_clusters)
            return status_cluster, edc_dis

    @staticmethod
    def cluster_k_mean(movies_plot, c_role, status, min_threshold=10, n_clusters=25):
        # find target cluster number

        status_cluster = {}
        status_list = []
        project_id_list = []

        for p_i in movies_plot.keys():
            movie_plot = movies_plot[p_i]
            movie_status = movie_plot.down_sample_status
            char_index = movie_plot.char_role_dict[c_role]
            for c_i in char_index:
                cur_status = movie_status[c_i][status]
                status_list.append(cur_status)
                project_id_list.append(p_i)
            # compare_cluster(status_cluster, movie_status, p_i, char_index, status, min_threshold)
        kmeans = KMeans(n_clusters=n_clusters)
        X = np.array(status_list)
        kmeans.fit(X)
        centroids = kmeans.cluster_centers_
        labels = kmeans.labels_

        for i, p_id in enumerate(project_id_list):
            movie_plot = movies_plot[p_id]
            char_index = movie_plot.char_role_dict[c_role]
            movie_status = movie_plot.down_sample_status
            for c_i in char_index:
                if labels[i] not in status_cluster.keys():
                    status_cluster[labels[i]] = Cluster(movie_status[c_i][status], p_id)
                    # status_cluster[labels[i]].update_average_cluster(centroids[labels[i]])
                else:
                    status_cluster[labels[i]].update_cluster(movie_status[c_i][status], p_id)
        return status_cluster, min_threshold


class Cluster:
    def __init__(self, cluster, project_id):
        self.cluster = cluster
        self.contain = [cluster]
        self.project_ids = [project_id]

    def update_cluster(self, cluster, p_id):
        self.contain.append(cluster)
        cluster_sum = np.zeros(cluster.shape)
        for _cluster in self.contain:
            cluster_sum += _cluster
        self.cluster = cluster_sum/len(self.contain)
        self.project_ids.append(p_id)

    def update_average_cluster(self, cluster):
        self.cluster = cluster

    def cluster_plot(self, c_role, status_index):
        x = np.arange(0, len(self.cluster))
        for status in self.contain:
            if np.sum(status) != 0 and np.sum(status) != status.shape[0]*9:
                plt.plot(x, status, c=np.random.rand(3, ))

        path_all_plot = "data/plot_data/{c_role}/status_{st_id}/all_plot/"\
            .format(c_role=c_role, st_id=status_index)
        path_cluster_rep = "data/plot_data/{c_role}/status_{st_id}/cluster_average_rep/"\
            .format(c_role=c_role, st_id=status_index)

        Path(path_all_plot).mkdir(parents=True, exist_ok=True)
        Path(path_cluster_rep).mkdir(parents=True, exist_ok=True)

        plt.title('Cluster ID:{cluster_id} Status:{status_index} Plot, {movie_num} Movies in this Cluster '
                  .format(cluster_id=self.project_ids[0], status_index=status_index, movie_num=len(self.project_ids)))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.ylim(0, 4)
        plt.savefig(path_all_plot + 'cluster_{cluster_id}_movies_status{status_index}.png'
                    .format(cluster_id=self.project_ids[0], status_index=status_index))

        plt.clf()
        plt.plot(x, self.cluster, c=np.random.rand(3, ), marker=next(marker))
        plt.title('Cluster ID:{cluster_id}, Status:{status_index} Representation Plot, '
                  '{movie_num} Movies in this Cluster'
                  .format(cluster_id=self.project_ids[0], status_index=status_index, movie_num=len(self.project_ids)))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.ylim(0, 4)
        plt.savefig(path_cluster_rep + 'cluster_{cluster_id}_rep_movies_status{status_index}.png'
                    .format(cluster_id=self.project_ids[0], status_index=status_index))
        plt.clf()