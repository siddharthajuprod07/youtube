import requests as req
import json

def tmdb_api_call(requestURL,parameters):
    response = req.get(url=requestURL,params=parameters)
    if response.status_code != 200:
        print(response.json())
        exit()
    data = response.json()
    return json.dumps(data)

def get_upcoming_movies_by_page(api_key, page_number=1):
    requestURL = "https://api.themoviedb.org/3/movie/upcoming"
    parameters = {"api_key" : api_key, "page" : page_number }
    return tmdb_api_call(requestURL, parameters)
    
def main():
    api_key = "733ac994290c6f277b11565f26ebe1cb"
    upcoming_movie_list = get_upcoming_movies_by_page(api_key,1)
    data = json.loads(upcoming_movie_list)
    print(json.dumps(data["results"]))


main()

