import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from general.tools import get_index_positions
from general.save_load import SaveBasic


class Movie:
    url = ""
    down_sample_status = None
    resample_status = None

    char_index = []
    char_role_label = []

    def __init__(self, m_id, m_name, p_id, p_name, chars_num, chars_role, status):
        self.m_id = m_id
        self.m_name = m_name
        self.p_id = p_id
        self.p_name = p_name
        self.characters_num = chars_num
        self.char_role_dict = chars_role
        self.movie_status = status

        self.initial_url()
        self.char_index = []
        self.char_role_label = []
        self.add_char_role_label()

    def initial_url(self):
        self.url = 'http://story.minestoryboard.com/#/SpecifyCharacters/{p_id}'.format(p_id=self.p_id)

    def add_char_role_label(self):
        for char_role in self.char_role_dict.keys():
            for i, c_i in enumerate(self.char_role_dict[char_role]):
                self.char_index.append(c_i)
                self.char_role_label.append(char_role + str(i))

    def resample_scene_length(self, status_num, scene_max_length):
        resampled_movie_status = np.zeros((self.characters_num, status_num, scene_max_length))
        single_occ = int(scene_max_length / self.movie_status.shape[-1])
        addition_occ = scene_max_length % self.movie_status.shape[-1]
        for c_i in range(self.movie_status.shape[0]):
            for st_i in range(self.movie_status.shape[1]):
                addition_occ_p = 0
                start = 0
                for s_i in range(self.movie_status.shape[2]):
                    end = start + single_occ
                    if addition_occ_p < addition_occ:
                        end += 1
                    resampled_movie_status[c_i][st_i][start:end] = self.movie_status[c_i][st_i][s_i]
                    start = end
                    addition_occ_p += 1
        self.resample_status = resampled_movie_status

    def down_sample_v2(self, n=100):
        labels = ['health', 'attitude', 'change', 'crisis', 'goal']

        resample_len = self.resample_status.shape[-1]
        self.down_sample_status = np.zeros((self.resample_status.shape[0], self.resample_status.shape[1], n))

        # initial start and end
        status_pool = np.full((self.resample_status.shape[0], self.resample_status.shape[1], n), None)
        for c_i in range(self.resample_status.shape[0]):
            for st_i in range(self.resample_status.shape[1]):
                self.down_sample_status[c_i][st_i][0] = self.resample_status[c_i][st_i][0]
                self.down_sample_status[c_i][st_i][-1] = self.resample_status[c_i][st_i][-1]
                status_pool[c_i][st_i][0] = [int(self.resample_status[c_i][st_i][0])]
                status_pool[c_i][st_i][-1] = [int(self.resample_status[c_i][st_i][-1])]

        # rest status
        r_n = n - 2
        adder = int((resample_len-2)/r_n)
        r_resmaple_status = self.resample_status[:, :, 1:-1]

        for c_i in range(self.resample_status.shape[0]):
            for st_i in range(self.resample_status.shape[1]):
                start = 1
                cur_end = start
                end = resample_len - 1
                r_n_p = 1
                cur_status = r_resmaple_status[c_i][st_i].tolist()
                while cur_end + adder < end:
                    cur_end = start + adder
                    cur_status_pool = []
                    for i in range(start, cur_end):
                        status = cur_status[i]
                        if status not in cur_status_pool:
                            cur_status_pool.append(int(status))
                    status_pool[c_i][st_i][r_n_p] = cur_status_pool
                    start = cur_end
                    r_n_p += 1

        for c_i in range(self.resample_status.shape[0]):
            for st_i in range(self.resample_status.shape[1]):
                print('char {} {} : select pool = {}'.format(c_i, labels[st_i], status_pool[c_i][st_i].tolist()))



        pass

    def down_sample_strict(self, n=100):
        resample_len = self.resample_status.shape[-1]
        adder = int(resample_len/n)
        self.down_sample_status = np.zeros((self.resample_status.shape[0], self.resample_status.shape[1], n))
        for c_i in range(self.resample_status.shape[0]):
            for st_i in range(self.resample_status.shape[1]):
                cur_status = self.resample_status[c_i][st_i].tolist()
                turing_point_y = []
                turing_point_x = []
                for i, st in enumerate(cur_status):
                    if i == 0:
                        turing_point_x.append(0)
                        turing_point_y.append(st)
                    else:
                        if cur_status[i-1] != st:
                            turing_point_x.append(i / (len(cur_status) - resample_len%n))
                            turing_point_y.append(st)

                if len(turing_point_x) > n:
                    print('n < turning point, unable to down sample {}, try other n'.format(self.p_id))
                    # return
                fit_turning_point = [-1 for x in range(n)]
                fited_turing_point = [(False, 0) for x in range(n)]
                priority_order = []

                turing_point_y_rank = list(set(turing_point_y))
                start = 0
                end = len(turing_point_y_rank) - 1
                while True:
                    if len(priority_order) == len(turing_point_y_rank):
                        break
                    priority_order.append(turing_point_y_rank[end])
                    end -= 1
                    if len(priority_order) == len(turing_point_y_rank):
                        break
                    priority_order.append(turing_point_y_rank[start])
                    start += 1
                    if len(priority_order) == len(turing_point_y_rank):
                        break

                for lvl in priority_order:
                    if lvl not in turing_point_y:
                        continue
                    lv_index = get_index_positions(turing_point_y, lvl)
                    for i in lv_index:
                        index = int(turing_point_x[i] * n)
                        if index == 28:
                            index = 27
                        if not fited_turing_point[index][0]:
                            fit_turning_point[index] = turing_point_y[i]
                            fited_turing_point[index] = (True, turing_point_x[i])
                        elif turing_point_x[i] > fited_turing_point[index][1] and index + 1 <= len(fited_turing_point)-1\
                                and not fited_turing_point[index+1][0]:
                            fit_turning_point[index+1] = turing_point_y[i]
                            fited_turing_point[index+1] = (True, turing_point_x[i])
                        elif turing_point_x[i] < fited_turing_point[index][1] and not fited_turing_point[index-1][0]:
                            fit_turning_point[index - 1] = turing_point_y[i]
                            fited_turing_point[index - 1] = (True, turing_point_x[i])

                pointer = -1
                for s_i in range(n):
                    pointer += adder
                    if not fited_turing_point[s_i][0]:
                        self.down_sample_status[c_i][st_i][s_i] = self.resample_status[c_i][st_i][pointer]
                    else:
                        self.down_sample_status[c_i][st_i][s_i] = fit_turning_point[s_i]

    def plot_status(self, down_sample=False):
        if down_sample:
            sample_status = self.down_sample_status
            names = 'down_sample'
        else:
            sample_status = self.movie_status
            names = 'original'
        labels = ['health', 'attitude', 'change', 'crisis', 'goal']

        st_index_range = []
        for i in range(len(self.char_index)):
            st_index_range.append([4, 3, 1, 2, 0])

        color = ['r', 'g', 'y', 'navy', 'm']
        visual_bias = [0.06, 0.03, 0, -0.03, -0.06]

        for i, c_i in enumerate(self.char_index):
            x = np.arange(0, sample_status.shape[-1])
            fig, ax = plt.subplots()
            for st_i in st_index_range[c_i]:
                status = sample_status[c_i][st_i]
                if np.sum(status) == 0 or np.sum(status) == status.shape[0] * 9:
                    continue
                c = color[st_i]
                ax.scatter(x, status+visual_bias[st_i], s=10, c=c)
                ax.plot(x, status+visual_bias[st_i], c=c, label=labels[st_i])

            path_single_movie_plot = "data/single_movie/{p_id}/{sample}/".format(sample=names, p_id=self.p_id)
            Path(path_single_movie_plot).mkdir(parents=True, exist_ok=True)
            plt.title(
                'Character : {char_index} Status : {st_range}'
                .format(char_index=self.char_role_label[i], st_range=', '.join([str(x) for x in st_index_range[i]])))

            if down_sample:
                ax.set_xticks(x)
            plt.xlabel('time')
            plt.ylabel('level')
            plt.ylim(-0.5, 4.5)
            plt.xlim(-0.5, len(x))
            plt.legend()
            # if down_sample:
            plt.grid()
            plt.savefig(path_single_movie_plot + '{p_id}_{char_index}_'
                        .format(p_id=self.p_id, char_index=self.char_role_label[i]))
            plt.clf()

    def print_status_guide(self):
        labels = ['Health', 'Attitude', 'Change', 'Crisis', 'Goal']
        st_index_range = []
        for i in range(len(self.char_index)):
            st_index_range.append([4, 3, 1, 2, 0])
        path_single_movie_plot = "statistics_collection/plot_data/single_movie/{p_id}/{sample}/" \
            .format(sample='down_sample', p_id=self.p_id)

        Path(path_single_movie_plot).mkdir(parents=True, exist_ok=True)

        lines = []
        # basic format
        lines.append('# Project {} - {}'.format(self.p_id, self.p_name))
        lines.append('### Write by : ')
        lines.append('## {} Arcs'.format(self.m_name))
        lines.append('![{}]({})'.format(self.m_name, 'picture location'))
        lines.append('## Story Information')
        lines.append('### Theme\n\n')
        lines.append('### Character\n\n')
        lines.append('## Plot')

        for s_i in range(1, self.down_sample_status.shape[-1]):
            lines.append('\n### Scene {}'.format(s_i))
            for c_i in self.char_index:
                start_status = []
                end_status = []
                select_status = []
                for st_i in st_index_range[c_i]:
                    status = self.down_sample_status[c_i][st_i]
                    if np.sum(status) == 0 or np.sum(status) == status.shape[0] * 9:
                        continue
                    select_status.append(labels[st_i])
                    start_status.append(str(int(self.down_sample_status[c_i][st_i][s_i-1])))
                    end_status.append(str(int(self.down_sample_status[c_i][st_i][s_i])))

                lines.append('#### Character {c_i} : [{start}] -> [{end}]'
                             .format(c_i=c_i, start=' '.join(start_status), end=' '.join(end_status)))

        path_single_movie = "data/single_movie/{p_id}/".format(p_id=self.p_id)
        Path(path_single_movie).mkdir(parents=True, exist_ok=True)
        SaveBasic.save_basic(lines, 'guide.md', path_single_movie, file_type='txt', called='guide')


class MoviePlot:
    @staticmethod
    def plot_basic(x, y, p_id, fp=None, called=None):
        pass