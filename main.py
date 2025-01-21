import json
import os

import requests
from geopy import distance
from dotenv import load_dotenv
import folium
import time


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def create_map(coffee_shops, user_coords, file_name):
    user_latitude, user_longitude = user_coords
    coffee_map = folium.Map(location=[user_latitude, user_longitude])

    folium.Marker(
        location=[user_latitude, user_longitude],
        popup='Вы здесь',
        icon=folium.Icon(color='blue')
    ).add_to(coffee_map)

    for shop in coffee_shops:
        folium.Marker(
            location=[shop['latitude'], shop['longitude']],
            popup=f"{shop['title']}: {shop['distance']:.2f} км",
            icon=folium.Icon(color='green')
        ).add_to(coffee_map)

    coffee_map.save(file_name)


def main():
    with open("coffee.json", 'r', encoding="CP1251") as file:
        data = json.load(file)

    load_dotenv('.env')
    api_key = os.getenv('apikey')
    address = input("Где вы находитесь?")
    coords = fetch_coordinates(api_key, address)

    coffee_shops_info = []

    for coffee_shops in data:
        name = coffee_shops['Name']
        longitude = coffee_shops["Longitude_WGS84"]
        latitude = coffee_shops["Latitude_WGS84"]
        shop_coords = (latitude, longitude)
        distance_to_user = distance.distance(coords, shop_coords).km

        coffee_shops_info.append({
            'title': name,
            'distance': distance_to_user,
            'latitude': latitude,
            'longitude': longitude,
        })

    sorted_coffee_shops = sorted(coffee_shops_info, key=lambda x: x['distance'])
    coming_coffee_shops = sorted_coffee_shops[:5]

    timestamp = int(time.time())
    file_name = f'coffee_shops_map_{timestamp}.html'

    create_map(coming_coffee_shops, coords, file_name)


if __name__ == "__main__":
    main()
