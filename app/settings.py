import pathlib

APP_DIR = pathlib.Path(__file__).parent.resolve()

ROUTES_LINK = "https://gortrans74.ru/chelyabinsk/routes.txt"
STOPS_LINK = "https://gortrans74.ru/chelyabinsk/stops.txt"

# for local debug
# ROUTES_LINK = APP_DIR / "../routes.txt"
# STOPS_LINK = APP_DIR / "../stops.txt"

TRANSPORT_TYPE_NAMES = {
    "bus": "Автобус",
    "minibus": "Маршрутное такси",
    "tram": "Трамвай",
    "trol": "Троллейбус",
}

TRANSPORT_TYPE_COLORS = {
    "bus": [0, 89, 100, 0],
    "minibus": [0, 89, 100, 0],
    "tram": [0, 89, 100, 0],
    "trol": [0, 89, 100, 0],
}
