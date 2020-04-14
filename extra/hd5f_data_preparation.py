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
    if m_name_split[-2] == '--':
        m_name_split = m_name_split[:-1]
    m_name = ' '.join(m_name_split[:-1])
    if (df['title'] == m_name).any():
        rating = df.loc[(df['title'] == m_name)]['avg_rating'].values[0]
    else:
        if movie_name == '9 2009':
            return 7.1
        else:
            print(movie_name)
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