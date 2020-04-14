def filter_process(movies):
    filtered_movies = []
    for movie in movies:
        if not movie['movie'] or movie['id'] in [0]:
            continue
        filtered_movies.append(movie)
