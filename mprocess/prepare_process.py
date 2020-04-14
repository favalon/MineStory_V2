import numpy as np
from general.movies import Movie

STATUS_NUM = 5
RESAMPLE_LENGTH = 1000
MIN_THRESHOLD = 5


def resample_scene_length(movie_status, char_num, status_num, scene_max_length):
    resampled_movie_status = np.zeros((char_num, status_num, scene_max_length))
    single_occ = int(scene_max_length/movie_status.shape[-1])
    addition_occ = scene_max_length % movie_status.shape[-1]
    for c_i in range(movie_status.shape[0]):
        for st_i in range(movie_status.shape[1]):
            addition_occ_p = 0
            start = 0
            for s_i in range(movie_status.shape[2]):
                end = start + single_occ
                if addition_occ_p < addition_occ:
                    end += 1
                resampled_movie_status[c_i][st_i][start:end] = movie_status[c_i][st_i][s_i]
                start = end
                addition_occ_p += 1
    return resampled_movie_status


def process(projects, downsample=11):
    projects_by_id = {}
    prepared_projects_dict = {}
    for project in projects:
        p_id = project['id']
        projects_by_id[p_id] = project
        p_name = project['name']
        m_name = project['movie']['name']
        m_id = project['movie']['id']
        char_num = len(project['character_flag'])
        char_role_dict = {}
        for char in project['movie']['specify']['key_characters']:
            c_i = char['index']
            c_role = char['rule']
            if c_role in char_role_dict.keys():
                char_role_dict[c_role].append(c_i)
            else:
                char_role_dict[c_role] = [c_i]
        # health, mental_health, change, crisis, goal
        movie_status = np.zeros((char_num, STATUS_NUM, len(project['scene'])))
        for c_i in project['character_flag'].keys():
            for i, scene in enumerate(project['scene']):
                movie_status[int(c_i)][0][i] = scene['specify_data'][int(c_i)]['health']
                movie_status[int(c_i)][1][i] = scene['specify_data'][int(c_i)]['mental_health']
                movie_status[int(c_i)][2][i] = scene['specify_data'][int(c_i)]['change']
                movie_status[int(c_i)][3][i] = scene['specify_data'][int(c_i)]['crisis']
                movie_status[int(c_i)][4][i] = scene['specify_data'][int(c_i)]['goal']
        normalize_status_x = np.arange(movie_status.shape[-1], dtype=np.float32)
        normalize_status_x /= np.max(np.abs(normalize_status_x))

        prepared_project = Movie(m_id, m_name, p_id, p_name, char_num, char_role_dict, movie_status)
        prepared_project.resample_scene_length(STATUS_NUM, RESAMPLE_LENGTH)
        # prepared_project.down_sample_v2(n=downsample)
        prepared_project.down_sample_strict(n=downsample)
        prepared_projects_dict[p_id] = prepared_project
    return prepared_projects_dict, projects_by_id


if __name__ == '__main__':
    process()