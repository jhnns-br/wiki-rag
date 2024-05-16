# minimum client to test the API
# fastapi port is 8000

import requests

q = "<example question>"

response = requests.get(f"http://127.0.0.1:8000/chunks/{q}")
print(response.json())

response = requests.get(f"http://127.0.0.1:8000/answer/{q}")
print(response.json())