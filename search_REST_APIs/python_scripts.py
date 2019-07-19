import requests

data = {
  'id': 'mysearch_02151949',
  'max_count': '50000',
  'status_buckets': '300',
  'search':'search index=_internal sourcetype=splunkd'
}

response = requests.post('https://localhost:8089/servicesNS/admin/search/search/jobs', data=data, verify=False, auth=('admin', 'monitor!'))

print(response.text)
