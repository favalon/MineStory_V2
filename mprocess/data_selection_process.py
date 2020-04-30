

def process(min_movies_in_cluster, data):
    char_roles_index = {"MainCharacter": 0, "Supporter": 1, "Opposites": 2}

    selected = {}
    for ac in data.keys():
        role_data = data[ac]
        for status in role_data.keys():
            clusters = role_data[status]
            for cluster_id in clusters.keys():
                if 30 > len(clusters[cluster_id].project_ids) > min_movies_in_cluster:
                    for p_id in clusters[cluster_id].project_ids:
                        if p_id not in selected.keys():
                            selected[p_id] = [0, 0, 0, 0, 0]
                            selected[p_id][status] = 1
                        else:
                            selected[p_id][status] += 1

    d_list = []
    for p_id in selected.keys():
        if selected[p_id][4] == 0:
            d_list.append(p_id)
            continue
        count = 0
        if selected[p_id][1] == 0:
            count += 1
        if selected[p_id][2] == 0:
            count += 1
        if selected[p_id][3] == 0:
            count += 1
        if count > 1 :
            d_list.append(p_id)

    for p_id in d_list:
        del selected[p_id]

    return list(selected.keys())

if __name__ == '__main__':
    process()