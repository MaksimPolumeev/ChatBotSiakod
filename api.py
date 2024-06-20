import requests
import csv


api_key = '9035615b'

def get_movie_data(title):
    url = f'http://www.omdbapi.com/?t={title}&apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Ошибка при получении данных для фильма: {title}')
        return None

def write_to_csv(data, filename='movies.csv'):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        if csvfile.tell() == 0:
            writer.writerow(['movie_info'])

        for movie in data:
            movie_info = f"{movie['title']}, {movie['year']}, {movie['genre']}, {movie['rating']}, {movie['plot']}"
            writer.writerow([movie_info])


def main():

    url = f'http://www.omdbapi.com/?s=Drama&apikey={api_key}&type=movie&page=1'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        total_results = 15
        movies_data = []


        if total_results > 0:

            num_pages = min(total_results // 10 + 1, 20)
            for page in range(1, num_pages + 1):
                url = f'http://www.omdbapi.com/?s=Drama&apikey={api_key}&type=movie&page={page}'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('Response') == 'True':
                        movies = data.get('Search', [])
                        for movie in movies:
                            movie_title = movie.get('Title')
                            movie_data = get_movie_data(movie_title)
                            if movie_data and movie_data.get('Response') == 'True':
                                title = movie_data.get('Title')
                                year = movie_data.get('Year')
                                genre = movie_data.get('Genre')
                                rating = movie_data.get('imdbRating')
                                plot = movie_data.get('Plot')

                                movie_info = {
                                    'title': title,
                                    'year': year,
                                    'genre': genre,
                                    'rating': rating,
                                    'plot': plot
                                }
                                print(movie_info)
                                movies_data.append(movie_info)

        write_to_csv(movies_data)

    else:
        print(f'Ошибка при получении данных о фильмах: {response.status_code}')

if __name__ == '__main__':
    main()
