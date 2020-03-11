import requests

r = requests.get('https://localhost:8089/services/movie_count_by_lang?ln=fr', auth=('admin', '<password>'),verify=False)
print(r.text)