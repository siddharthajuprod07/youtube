import requests

r = requests.get('https://localhost:8089/services/movie_count_by_lang?ln=fr', auth=('admin', 'monitor!'),verify=False)
print(r.text)