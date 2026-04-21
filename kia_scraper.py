import requests as re
from lxml import html
import requests
import json
from urllib.parse import urljoin
from db import insert_dealers, create_db
import re

# URL of the webpage
# base_url = "https://www.kia.com/in/buy/find-a-dealer.html"

# Headers to mimic a browser request
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-modified-since': 'Tue, 21 Apr 2026 09:05:10 GMT',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
    # 'cookie': '__cf_bm=WxEIMxACLFxBotbgIz2jD7Gv0TdMnWyNwoYLaxgZJJo-1776764585.4442217-1.0.1.1-KA_3_38ztuR_UAtAf49ZzkEEoRlyeSwkHRlq67ntXGOG_Ap7hgsKbb9Nm6vZuCtkmxhxQXvhZCpyjjjr2zpYReXbDKzY_xUVyAcBfMFCvtRdtvgQ0sA264RiChSLVWDy; _gcl_au=1.1.1332815290.1776764587; _fbp=fb.1.1776764587124.73407193912241996; _uetsid=806e95303d6611f19ddcb7e214758e97; _uetvid=806ec5c03d6611f185563787d5a46be2; _ga=GA1.1.593237707.1776764588; _twpid=tw.1776764588116.925023245579413316; _ga_9PSV9LG5D2=GS2.1.s1776764587$o1$g0$t1776764595$j52$l0$h0; cookie-agree=true',
}

# Send GET request to fetch the webpage content
# response = re.get(base_url, headers=headers)

# Check if the request was successful (status code 200)
# if response.status_code == 200:
    # Save the response content as an HTML file
    # with open('yallamotor_used_cars.html', 'w', encoding='utf-8') as file:
        # file.write(response.text)
    # print("HTML file has been saved successfully.")
# else:
    # print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# STEP 1: STATE + CITY
def get_state_city():
    url = "https://www.kia.com/api/kia2_in/findAdealer.getStateCity.do"

    res = requests.get(url, headers=headers)
    json_data = res.json()

    state_city_data = json_data.get("data").get("stateAndCity")

    all_locations = []

    for item in state_city_data:
        state_info = item.get("val1")
        cities = item.get("val2")

        state = state_info.get("value")
        state_key = state_info.get("key")

        for city in cities:
            all_locations.append({
                "state": state,
                "state_key": state_key,
                "city": city.get("value "),
                "city_key": city.get("key")
            })

    return all_locations


# STEP 2: DEALER API
def get_dealers(state_key, city_key):
    url = "https://www.kia.com/api/kia2_in/findAdealer.getDealerList.do"

    # this API expects FORM DATA (not JSON)
    payload = {
        "state": state_key,
        "city": city_key
    }

    res = requests.post(url, data=payload, headers=headers)

    try:
        return res.json()
    except:
        print("Invalid JSON response")
        return {}


# STEP 3: LOOP
def process_all():
    locations = get_state_city()

    all_dealers = []

    for i, loc in enumerate(locations):
        print(f"Processing {i+1}/{len(locations)} -> {loc['state']} - {loc['city']}")

        data = get_dealers(loc.get("state_key"), loc.get("city_key"))

        dealers = data.get("data") 

        for d in dealers:
            all_dealers.append({
                "state": loc.get("state"),
                "city": loc.get("city"),

                "name": d.get("dealerName"),   
                "address": " ".join([
                    d.get("address1", ""),
                    d.get("address2", ""),
                    d.get("address3", "")
                ]).strip(),

                "phone": (d.get("phone1") or d.get("phone2")),
                "email": d.get("email"),
                "website": d.get("website")
            })

    return all_dealers

if __name__ == "__main__":
    data = process_all ()

    print("\nTotal Dealers:", len(data))

    with open("kia_dealers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    create_db()
    insert_dealers(data)
    print("Data saved to kia_dealers.json")

    # OUTPUT :
    # Total Dealers: 1140
    # 1140 records inserted
    # Data saved to kia_dealers.json