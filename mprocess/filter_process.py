import numpy as np


def get_status_flag(character):
    character_index = character['index']
    character_class_flag = '{health}{attitude}{change}{crisis}{goal}' \
        .format(health=character['flag_health'], attitude=character['flag_mental_health'],
                change=character['flag_change'], crisis=character['flag_crisis'],
                goal=character['flag_goal'])
    return character_index, character_class_flag


def correct_scene_data(scenes, character):
    # ========= clean data base on flag information ============
    for i, scene in enumerate(scenes):
        s_c_i = character['index']
        if character['flag_health'] == 0:
            scenes[i]['specify_data'][s_c_i]['health'] = 9
        if character['flag_mental_health'] == 0:
            scenes[i]['specify_data'][s_c_i]['mental_health'] = 9
        if character['flag_change'] == 0:
            scenes[i]['specify_data'][s_c_i]['change'] = 9
        if character['flag_crisis'] == 0:
            scenes[i]['specify_data'][s_c_i]['crisis'] = 9
        if character['flag_goal'] == 0:
            scenes[i]['specify_data'][s_c_i]['goal'] = 9


def add_role_status_dict(project):
    characters = project['movie']['specify']['key_characters']
    for character in characters:
        correct_scene_data(project['scene'], character)
        char_index, char_flag = get_status_flag(character)
        project['{role}_flag'.format(role=character['rule'])] = {char_index: char_flag}
        if 'character_flag' in project.keys():
            project['character_flag'][char_index] = char_flag
        else:
            project['character_flag'] = {char_index:char_flag}


def story_first_process(project):
    STATUS = ['health', 'mental_health', 'change', 'crisis', 'goal']
    flag = np.full((len(project['character_flag'].keys()), len(STATUS)), 1)
    for c_i in project['character_flag'].keys():
        for st_i, status in enumerate(STATUS):
            for s_i in range(1, len(project['scene'])):
                if s_i == len(project['scene'])-1 and project['scene'][s_i]['specify_data'][c_i][status] == project['scene'][s_i-1]['specify_data'][c_i][status]:
                    flag[c_i][st_i] = 0
                if project['scene'][s_i]['specify_data'][c_i][status] == project['scene'][s_i-1]['specify_data'][c_i][status]:
                    continue
                else:
                    break

        if 'story_first_character_flag' not in project:
            project['story_first_character_flag'] = {}
            char_class = flag[c_i].tolist()
            char_class = list(map(str, char_class))
            project['story_first_character_flag'][c_i] = ''.join(char_class)
        else:
            char_class = flag[c_i].tolist()
            char_class = list(map(str, char_class))
            project['story_first_character_flag'][c_i] = ''.join(char_class)


def process(movies):
    filtered_movies = []
    for movie in movies:
        if not movie['movie'] or movie['id'] in [0, 123, 163 ,253]:
            continue
        filtered_movies.append(movie)

    for movie in filtered_movies:
        add_role_status_dict(movie)

    # ===== story manager first (smf) data ===========
    movies_smf = filtered_movies
    for movie in movies_smf:
        story_first_process(movie)

    return movies_smf
