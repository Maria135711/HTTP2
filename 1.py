import sys
from io import BytesIO  # Этот класс поможет нам сделать картинку из потока байт
from map_utils import calculate_spn, calculate_bbox
import requests
from PIL import Image


def main():
    # Пусть наше приложение предполагает запуск:
    # python search.py Москва, ул. Ак. Королева, 12
    # Тогда запрос к геокодеру формируется следующим образом:
    # toponym_to_find = " ".join(sys.argv[1:])
    toponym_to_find = "Москва, ул. Адмирала Руднева 8, 12"
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "6efcb3a6-70e4-4738-abdf-e75aa2835e20",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        print("Ошибка выполнения запроса:")
        print(response.url)

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    address_pos = toponym["Point"]["pos"].split()
    address_ll = ",".join(address_pos)
    address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
    delta = "0.005"
    apikey = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    spn = calculate_spn(toponym)
    # Собираем параметры для запроса к StaticMapsAPI:
    search_params = {
        "text": "аптека",
        "lang": "ru_RU",
        "ll": address_ll,
        "rescale": 1,
        "type": "biz",
        "apikey": apikey,

    }

    search_api_server = "https://search-maps.yandex.ru/v1"
    response = requests.get(search_api_server, params=search_params)
    try:
        json_response = response.json()
        pharmacy = json_response["features"][0]
        pharmacy_pos = list(map(str, pharmacy["geometry"]["coordinates"]))
        pharmacy_ll = ",".join(pharmacy_pos)
        pharmacy_name = pharmacy["properties"]["name"]
        pharmacy_address = pharmacy["properties"]["CompanyMetaData"]["address"]
        pharmacy_hours = pharmacy["properties"]["CompanyMetaData"].get("Hours", {}).get("text", "нет информации")
    except (KeyError, IndexError):
        print("Не найдено аптек поблизости")
        return

    route_api_server = "https://api.routing.yandex.net/v2/distancematrix"
    route_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "origins": address_ll,
        "destinations": pharmacy_ll,
        "mode": "walking"
    }
    response = requests.get(route_api_server, params=route_params)
    distance = response.json()["rows"][0]["elements"][0]["distance"]["text"]
    print("\nНайденная аптека:")
    print(f"Название: {pharmacy_name}")
    print(f"Адрес: {pharmacy_address}")
    print(f"Режим работы: {pharmacy_hours}")
    print(f"Расстояние от '{address}': {distance}\n")
    map_api_server = "https://static-maps.yandex.ru/1.x/"
    map_params = {
        "l": "map",
        "pt": f"{address_pos[0]},{address_pos[1]},pm2dgl~{pharmacy_pos[0]},{pharmacy_pos[1]},pm2bgl",
        "bbox": calculate_bbox([address_pos, pharmacy_pos]),
        "apikey": "65ff937e-7030-4077-b49f-16a9183354c4"
    }

    response = requests.get(map_api_server, params=map_params)
    if response.ok:
        Image.open(BytesIO(response.content)).show()
    else:
        print("Ошибка получения карты:", response.status_code)


if __name__ == "__main__":
    main()
