import requests
import json
from bs4 import BeautifulSoup

deputy_data = {}

for i in range(1, 461):
  deputy_id = str(i)
  if i < 100:
    deputy_id = "0" + deputy_id
    if i< 10:
      deputy_id = "0" + deputy_id
  address = f"https://www.sejm.gov.pl/sejm9.nsf/posel.xsp?id={deputy_id}&type=A"
  response = requests.get(address)
  soup = BeautifulSoup(response.content, parser="html.parser")
  name = soup.find("h1").text
  party_data = soup.find("ul", class_="data")
  party_name = list(list(party_data.children)[1].children)[1].text
  if name in deputy_data:
    print("DUPLICATE")
  deputy_data[name] = party_name

with open("deputies.json", "w") as f:
  json.dump(deputy_data, f, indent=2, ensure_ascii=False)
