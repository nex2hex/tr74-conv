import pathlib

APP_DIR = pathlib.Path(__file__).parent.resolve()

CACHE_DIR = APP_DIR / "../cache/"
CACHE_DIR.mkdir(exist_ok=True)

ROUTES_LINK = "https://gortrans74.ru/chelyabinsk/routes.txt"
ROUTES_FILE = CACHE_DIR / "routes.txt"

STOPS_LINK = "https://gortrans74.ru/chelyabinsk/stops.txt"
STOPS_FILE = CACHE_DIR / "stops.txt"

ROUTES_DATAFRAME_CACHE = CACHE_DIR / "routes_dataframe.pickle"

TRANSPORT_TYPE_NAMES = {
    "bus": "Автобус",
    "minibus": "Маршрутное такси",
    "tram": "Трамвай",
    "trol": "Троллейбус",
    "seasonalbus": "Автобус",
}

TRANSPORT_TYPE_COLORS = {
    "bus": [85, 22, 100, 13],
    "minibus": [85, 22, 100, 13],
    "tram": [0, 89, 100, 0],
    "trol": [0, 89, 100, 0],
    "seasonalbus": [85, 22, 100, 13],
}
