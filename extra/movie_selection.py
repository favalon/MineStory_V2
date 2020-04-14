import pandas as pd
import os
import numpy as np
from general.save_load import SaveBasic, LoadBasic


def read_file(fp, sheet_name):
    if os.path.isfile(fp):
        xl = pd.ExcelFile(fp)
        print(xl.sheet_names)
        df = xl.parse(sheet_name)
        return df
    else:
        raise EOFError


def save_file(fp, df):
    df.to_excel(fp)


def split_excel(df, size, new_fp):
    i = 0
    for chunk in np.split(df, len(df) // size):
        chunk.to_excel(new_fp+'{:02d}.xlsx'.format(i), index=False)
        i += 1


def select_movie(df, u_nl):
    age_list = ['3+', '4+', '5+', '6+', '7+', '8+', '9+', '10+']
    new_df = df.loc[(df['age'].isin(age_list)) & (df['avg_rating'] <= 4.8) & (~df['title'].isin(u_nl))]
    print(new_df)
    return new_df


def used_movies():
    from datetime import date
    date = '2020-03-19'
    data_fp = '../data/{}/'.format(date)
    projects = LoadBasic.load_basic('ori_projects_data', path=data_fp, called='used_movies')
    used_name_list = []
    for project in projects:
        m_name_split = project['movie']['name'].strip().split(' ')
        m_name = ' '.join(m_name_split[:-1])
        print(m_name)
        used_name_list.append(m_name)
    return used_name_list


def main():
    fp = 'movie_list.xlsx'
    n_fp = 'filtered_movie_list.xlsx'
    sn = 'Release Candidate_20200220'

    u_nl = used_movies()

    df = read_file(fp, sn)
    new_df = select_movie(df, u_nl)
    save_file(n_fp, new_df)
    # split_excel(new_df, 50, n_fp)
    pass


if __name__ == '__main__':
    main()