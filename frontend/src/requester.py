# minimal client to test the connection

import requests

question = "<some question>"
r = requests.get(f"http://<server ip>:8000/chunks/{question}")
rj = r.json()

print(rj)