import json
import typing as t

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import utils
from .settings import APP_DIR, TRANSPORT_TYPE_NAMES

app = FastAPI()

app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    df_routes = utils.get_routes_dataframe()

    # list of all stops
    all_stops_list = []
    for _, item in df_routes.iterrows():
        all_stops_list += item["RouteStopsList"]
    all_stops_list = sorted(list(set(all_stops_list)))

    return templates.TemplateResponse(request=request, name="index.html", context={"all_stops_list": all_stops_list})


@app.post("/get_data")
def get_data(request: Request, stop_name: t.Annotated[str, Form()]):
    df_routes = utils.get_routes_dataframe()
    df_routes_with_stop = df_routes[df_routes["RouteStopsStr"].str.contains(f"#{stop_name}#")]

    result = {"data": []}
    for _, row in df_routes_with_stop.iterrows():
        payload = utils.get_json_payload(stop_name, row)
        if payload:
            result["data"].append(
                {
                    "name": f"{TRANSPORT_TYPE_NAMES[row['Transport']]} {row['RouteNum']}: {row['RouteName']}",
                    "payload": payload,
                    "payload_rendered": json.dumps(payload, indent=4, ensure_ascii=False).encode("utf8"),
                }
            )

    return result
