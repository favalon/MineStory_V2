from general.save_load import SaveBasic, LoadBasic
import os
import pandas as pd


def read_file(fp, sheet_name):
    if os.path.isfile(fp):
        xl = pd.ExcelFile(fp)
        print(xl.sheet_names)
        df = xl.parse(sheet_name)
        return df
    else:
        raise EOFError


def get_rating(movie_name, df):
    rating = 0
    m_name_split = movie_name.strip().split(' ')
    if len(m_name_split) > 2 and m_name_split[-2] == '--':
        m_name_split = m_name_split[:-1]
    m_name = ' '.join(m_name_split[:-1])
    if (df['title'] == m_name).any():
        rating = df.loc[(df['title'] == m_name)]['avg_rating'].values[0]
    else:
        if movie_name == '9 2009':
            return 7.1
        else:
            print(m_name)
    return rating


def save_hd5f(projects, path, fn, called=None):
    import numpy as np
    main_char = []
    sup_char = []
    opp_char = []

    main_char_down = []
    sup_char_down = []
    opp_char_down = []

    # open rating dict
    fp = 'extra/movie_list.xlsx'
    sn = 'rating'
    df = read_file(fp, sn)

    for p_id in projects.keys():
        project = projects[p_id]
        movie_rating = get_rating(project.m_name, df)
        if 'MainCharacter' in project.char_role_dict.keys():
            for i in project.char_role_dict['MainCharacter']:
                target = np.full((5, 65), -1)
                status = project.movie_status[i]
                target[:status.shape[0], :status.shape[1]] = status
                main_char.append((target, movie_rating))
                main_char_down.append((project.down_sample_status[i], movie_rating))
        if 'Supporter' in project.char_role_dict.keys():
            for i in project.char_role_dict['Supporter']:
                target = np.full((5, 65), -1)
                status = project.movie_status[i]
                target[:status.shape[0], :status.shape[1]] = status
                sup_char.append((target, movie_rating))
                sup_char_down.append((project.down_sample_status[i], movie_rating))
        if 'Opposites' in project.char_role_dict.keys():
            for i in project.char_role_dict['Opposites']:
                target = np.full((5, 65), -1)
                status = project.movie_status[i]
                target[:status.shape[0], :status.shape[1]] = status
                opp_char.append((target, movie_rating))
                opp_char_down.append((project.down_sample_status[i], movie_rating))

    import numpy as np
    main_char = np.array(main_char)
    sup_char = np.array(sup_char)
    opp_char = np.array(opp_char)
    main_char_down = np.array(main_char_down)
    sup_char_down = np.array(sup_char_down)
    opp_char_down = np.array(opp_char_down)

    SaveBasic.save_obj(main_char, path=path, fn='main_char', called=called)
    SaveBasic.save_obj(sup_char, path=path, fn='sup_char', called=called)
    SaveBasic.save_obj(opp_char, path=path, fn='opp_char', called=called)
    SaveBasic.save_obj(main_char_down, path=path, fn='main_char_down', called=called)
    SaveBasic.save_obj(sup_char_down, path=path, fn='sup_char_down', called=called)
    SaveBasic.save_obj(opp_char_down, path=path, fn='opp_char_down', called=called)


    # SaveBasic.save_hd5f(main_char, sup_char, opp_char,
    #                     data_name=['MainCharacter', 'Supporter', 'Opposites'],
    #                     path=path, fn=fn, called=called)
    # SaveBasic.save_hd5f(main_char_down, sup_char_down, opp_char_down,
    #                     data_name=['MainCharacter_down', 'Supporter_down', 'Opposites_down'],
    #                     path=path, fn=fn+'_down', called=called)

    pass


class DataHelper:
    @staticmethod
    def get_name_list(project, flag='project'):
        n_list = []
        if flag == 'project':
            for cur_project in project:
                # movie_name = ' '.join(cur_project['movie']['name'].strip().split(' ')[:-1])
                movie_name = cur_project['movie']['name'].strip()
                # print(movie_name)
                n_list.append(movie_name)

        return n_list

    @staticmethod
    def find_missing_score(n_list):
        fp = '../extra/movie_list.xlsx'
        sn = 'rating'
        df = read_file(fp, sn)
        for name in n_list:
            movie_rating = get_rating(name, df)

    @staticmethod
    def split_project_by_score(project, lt, ht):
        fp = 'extra/movie_list.xlsx'
        sn = 'rating'
        negative = {}
        neutral = {}
        positive = {}
        df = read_file(fp, sn)
        for p_id in project.keys():
            cur_project = project[p_id]
            movie_name = cur_project.m_name.strip()
            movie_rating = float(get_rating(movie_name, df))
            if movie_rating < lt:
                negative[p_id] = cur_project
            elif lt <= movie_rating < ht:
                neutral[p_id] = cur_project
            else:
                positive[p_id] = cur_project

        return negative, neutral, positive

    @staticmethod
    def create_data(projects, sample_num, label=-1, path=None, save=True):
        import numpy as np
        num_movie = len(projects)
        num_char_type = 3
        num_att = 5
        num_stage = 100
        arcs = np.full((num_movie, num_char_type, num_att, num_stage), -1)
        down_arcs = np.full((num_movie, num_char_type, num_att, sample_num), -1)
        label = label

        m_i = 0
        for p_id in projects.keys():
            project = projects[p_id]
            m_id = project.m_id
            if 'MainCharacter' in project.char_role_dict.keys():
                for i in project.char_role_dict['MainCharacter']:
                    target = np.full((5, num_stage), -1)
                    status = project.movie_status[i]
                    target[:status.shape[0], :status.shape[1]] = status
                    # target[target == 9] = 0
                    arcs[m_i, 0, :, :] = target
                    down_sample = project.down_sample_status[i]
                    # down_sample[down_sample == 9] = 0
                    down_arcs[m_i, 0, :, :] = down_sample
            if 'Supporter' in project.char_role_dict.keys():
                for i in project.char_role_dict['Supporter']:
                    target = np.full((5, num_stage), -1)
                    status = project.movie_status[i]
                    target[:status.shape[0], :status.shape[1]] = status
                    # target[target == 9] = 0
                    arcs[m_i, 1, :, :] = target
                    down_sample = project.down_sample_status[i]
                    # down_sample[down_sample == 9] = 0
                    down_arcs[m_i, 1, :, :] = down_sample
            if 'Opposites' in project.char_role_dict.keys():
                for i in project.char_role_dict['Opposites']:
                    target = np.full((5, num_stage), -1)
                    status = project.movie_status[i]
                    target[:status.shape[0], :status.shape[1]] = status
                    # target[target == 9] = 0
                    arcs[m_i, 2, :, :] = target
                    down_sample = project.down_sample_status[i]
                    # down_sample[down_sample == 9] = 0
                    down_arcs[m_i, 2, :, :] = down_sample
            m_i += 1
        if path is not None and save:
            from datetime import date
            from pathlib import Path
            date = date.today()
            # fp = Path((path + 'movie_label_{}_extended').format(label))
            fp_down = Path((path + 'movie_label_{}_down_{}').format(label, sample_num))
            # np.save(fp, arcs)
            np.save(fp_down, down_arcs)


def main(sample_num=15):
    from datetime import date
    date = date.today()
    data_fp = 'data/{}/'.format(date)
    all_project = LoadBasic.load_basic('prepared_project_data', path=data_fp)
    # project_name_list = DataHelper.get_name_list(all_project, flag='project')
    negative, neutral, positive = DataHelper.split_project_by_score(all_project, 6, 7.5)
    DataHelper.create_data(negative, sample_num, label=0, path=data_fp, save=True)
    DataHelper.create_data(neutral, sample_num, label=1, path=data_fp, save=True)
    DataHelper.create_data(positive, sample_num, label=2, path=data_fp, save=True)
    pass


def selected_main(selected_list, sample_num=15):
    from datetime import date
    date = date.today()
    data_fp = 'data/{}/'.format(date)
    all_project = LoadBasic.load_basic('prepared_project_data', path=data_fp)
    selected_project = {}
    for p_id in all_project.keys():
        if p_id in selected_list:
            selected_project[p_id] = all_project[p_id]
    negative, neutral, positive = DataHelper.split_project_by_score(selected_project, 6, 7.5)
    DataHelper.create_data(negative, sample_num, label=0, path=data_fp, save=True)
    DataHelper.create_data(neutral, sample_num, label=1, path=data_fp, save=True)
    DataHelper.create_data(positive, sample_num, label=2, path=data_fp, save=True)
    pass


if __name__ == '__main__':
    main()