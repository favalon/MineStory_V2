import os
from datetime import date
from transitions import Machine
from pathlib import Path
from extra.hd5f_data_preparation import save_hd5f
from general.save_load import SaveBasic, LoadBasic
from general import tools
from mprocess.filter_process import process as filter_process
from mprocess.prepare_process import process as prepare_process
from mprocess.cluster_process import process as cluster_process
from mprocess.plot_process import process as plot_process


class MineStory:
    date = date.today()
    data_fp = 'data/{}/'.format(date)

    states = ['start', 'filtering', 'end']
    projects = None
    projects_by_id = None
    filtered_projects = None
    prepared_projects = None
    role_clusters = {}

    char_roles_index = {"MainCharacter": 0, "Supporter": 1, "Opposites": 2}
    CLUSTER_NUM = [[25, 15, 10, 10, 5], [15, 8, 8, 8, 8], [5, 5, 5, 5, 5]]

    def __init__(self, data_url=None, data_path=None):
        self.data_url = data_url
        self.data_path = data_path
        # self.machine = Machine(model=self, states=MineStory.states, initial='start')
        # self.machine.add_transition(trigger='t_get_ori_project', source='start', dest='filtering', before='get_ori_project')
        # self.machine.add_transition(trigger='t_filters_movie', source='filtering', dest='end')

    def get_ori_project(self, save=False, use_load=False):
        if use_load:
            self.projects = LoadBasic.load_basic('ori_projects_data',
                                 path=self.data_fp, called='get_ori_project')
        else:
            self.projects = tools.get_data_url(self.data_url)
        if save:
            SaveBasic.save_basic(self.projects, 'ori_projects_data',
                                 path=self.data_fp, called='get_ori_project')

    def filter_project(self, save=False, use_load=False):
        if use_load:
            self.projects = LoadBasic.load_basic('ori_projects_data',
                                                          path=self.data_fp, called='filter_project')

        self.filtered_projects = filter_process(self.projects)
        if save:
            SaveBasic.save_basic(self.filtered_projects, 'filtered_projects_data',
                                 path=self.data_fp, called='filter_project')

    def reshape_project(self, save=False, use_load=False, hdf5=False):
        if use_load:
            self.filtered_projects = LoadBasic.load_basic('filtered_projects_data',
                                                          path=self.data_fp, called='reshape_project')

        self.prepared_projects, self.projects_by_id = prepare_process(self.filtered_projects, downsample=11)
        if save:
            SaveBasic.save_basic(self.prepared_projects, 'prepared_project_data',
                                 path=self.data_fp, called='reshape_project')

        if hdf5:
            save_hd5f(self.prepared_projects, fn='reshaped_data.h5',
                      path=self.data_fp, called='reshape_project_h5')

    def cluster_project(self, char_roles=None, save=False):
        if char_roles != ['all'] and char_roles:
            active_clusters = []
            for char in char_roles:
                active_clusters.append(self.char_roles_index[char])
        elif char_roles == ['all']:
            active_clusters = [0, 1, 2]
            char_roles = ["MainCharacter", "Supporter", "Opposites"]
        else:
            return -1
        for ac in active_clusters:
            self.role_clusters[ac] = cluster_process(self.prepared_projects, char_roles[ac],
                                                     fp=self.data_fp, n_clusters=self.CLUSTER_NUM[ac])
            if save:
                SaveBasic.save_basic(self.role_clusters, '{}_clusters_data'.format(char_roles[ac]),
                                     path=self.data_fp, called='cluster_process:count_cluster')

    def plot_project(self, p_id=None, char_roles=None, down_sample=True, guide=False):
        self.prepared_projects = LoadBasic.load_basic('prepared_project_data', path=self.data_fp, called='plot_project')
        selected_project = self.prepared_projects[p_id]
        # selected_project.down_sample_v2(n=11)
        plot_process(self.prepared_projects, p_id, fp=self.data_fp, char_roles=char_roles, down_sample=down_sample, guide=guide)
        pass


def main():
    mine_story = MineStory(data_url="http://api.minestoryboard.com/get_projects_data")
    mine_story.get_ori_project(save=True)
    mine_story.filter_project(save=True)
    mine_story.reshape_project(save=True, use_load=False, hdf5=False)
    # mine_story.cluster_project(['all'], save=True)
    mine_story.plot_project(p_id=332, guide=True)
    pass


if __name__ == '__main__':
    main()