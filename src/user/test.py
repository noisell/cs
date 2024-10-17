# import requests
# token = 'y0_AgAEA7qkmMHZAAx50gAAAAERnbQCAAD3f0ZJwkBDMKcuhkPeuYGFwb9YSQ'
#
# res = requests.post(url='https://cloud-api.yandex.net/v1/telemost-api/conferences', headers={'Authorization': 'OAuth ' + token}, json={
#     "access_level": "PUBLIC",
#     "live_stream": {
#         "access_level": "PUBLIC",
#         "title": "Заголовок",
#         "description": "Описание"
#       }
# })
# if res.status_code == 201:
#     print(res.json())
# else:
#     print(res.text)