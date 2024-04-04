import pickle
import time
import typing as t
from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

from .settings import (
    ROUTES_DATAFRAME_CACHE,
    ROUTES_FILE,
    ROUTES_LINK,
    STOPS_FILE,
    STOPS_LINK,
    TRANSPORT_TYPE_COLORS,
    TRANSPORT_TYPE_NAMES,
)


def get_ttl_hash(seconds=3600) -> int:
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


@lru_cache()
def _get_routes_dataframe(ttl_hash: int, use_cache=True) -> pd.DataFrame:
    if use_cache and ROUTES_DATAFRAME_CACHE.exists():
        return pickle.loads(ROUTES_DATAFRAME_CACHE.read_bytes())

    source = ROUTES_FILE if ROUTES_FILE.exists() else ROUTES_LINK
    df_routes = pd.read_csv(source, sep=";")
    df_routes["TimeShift"] = df_routes["RouteNum"]

    mask_exclude = df_routes["TimeShift"].notnull() & df_routes["TimeShift"].str.contains(",")
    df_routes.loc[~mask_exclude, "TimeShift"] = np.nan

    mask_include = df_routes["RouteNum"].notnull() & df_routes["RouteNum"].str.contains(",")
    df_routes.loc[mask_include, "RouteNum"] = np.nan

    df_routes["TimeShift"] = df_routes["TimeShift"].bfill()
    df_routes.ffill(inplace=True)
    df_routes.drop_duplicates(inplace=True)

    source = STOPS_FILE if STOPS_FILE.exists() else STOPS_LINK
    df_stops = pd.read_csv(source, sep=";")

    df_stops["Lat"] = df_stops["Lat"] / 100000
    df_stops["Lng"] = df_stops["Lng"] / 100000

    df_stops_with_names = df_stops[~df_stops["Name"].isna()]
    df_stops_without_names = df_stops[df_stops["Name"].isna()]

    stop_by_id = {}
    distance = cdist(df_stops_without_names[["Lat", "Lng"]], df_stops_with_names[["Lat", "Lng"]], metric="euclidean")
    df_stops.loc[df_stops["Name"].isna(), "Name"] = df_stops_with_names["Name"].to_numpy()[distance.argmin(axis=1)]

    stop_by_id = {}
    for _, row in df_stops.iterrows():
        stop_by_id[row["ID"]] = row["Name"]

    df_routes["RouteStopsList"] = df_routes["RouteStops"].apply(lambda x: [stop_by_id.get(i, i) for i in x.split(",")])
    df_routes["RouteStopsStr"] = df_routes["RouteStopsList"].apply(lambda x: "#" + "#".join(x) + "#")
    df_routes["temp"] = df_routes["TimeShift"].apply(lambda x: x.split(",,"))
    df_routes["TimeShiftOnRouteStart"] = df_routes["temp"].apply(lambda x: x[0])

    # ¯\_(ツ)_/¯ is't magic
    def time_ships_stops(x):
        res = [0]
        for item in x[4:]:
            if item:
                res.append(item.split(",")[0])
        return res

    df_routes["TimeShiftStops"] = df_routes["temp"].apply(time_ships_stops)

    df_routes.drop(labels=["temp"], axis=1, inplace=True)

    return df_routes


def get_routes_dataframe() -> pd.DataFrame:
    return _get_routes_dataframe(ttl_hash=get_ttl_hash())


def get_json_payload(stop_name: str, row: pd.Series) -> dict[str, t.Any]:
    has_working_days = "12345" in row["Weekdays"]
    has_sunday = "6" in row["Weekdays"]
    has_saturday = "7" in row["Weekdays"]
    has_low_floor = "z" in row["Weekdays"]

    stops_for_description = []
    for item in row["RouteStopsList"]:
        if len(item) <= 1 or item in stops_for_description:
            continue
        stops_for_description.append(item)

    stop_index = stops_for_description.index(stop_name) + 1
    stops_for_description = stops_for_description[stop_index:] or stops_for_description

    payload = {
        "head": {
            "type": TRANSPORT_TYPE_NAMES[row["Transport"]],
            "routeNumber": row["RouteNum"],
            "color": TRANSPORT_TYPE_COLORS[row["Transport"]],
            "direction": row["RouteName"].rsplit(" - ")[-1],
            "description": ", ".join(stops_for_description),
            "shiftMinutes": 0,
        },
        "commentBottom": [],
    }

    if not row["TimeShiftOnRouteStart"].startswith("-1,"):
        times_by_hour_working_days = {}
        times_by_hour_weekend = {}

        stop_index = row["RouteStopsList"].index(stop_name)
        stop_shift_in_minutes = 0
        stop_shift_in_minutes = sum(map(int, row["TimeShiftStops"][: stop_index + 1]))
        acc = None
        current_dict = times_by_hour_weekend

        for item in row["TimeShiftOnRouteStart"].split(","):
            item = item.replace("+", "")
            item = int(item)

            if item < 0:
                current_dict = times_by_hour_working_days

            if acc is None:
                acc = item
            else:
                acc += item

            hour = f"{(acc // 60):02d}"
            minute = f"{(acc % 60):02d}"

            if hour not in current_dict:
                current_dict[hour] = []

            current_dict[hour].append(minute)

        for item in (times_by_hour_working_days, times_by_hour_weekend):
            for _, v in item.items():
                if "" not in v:
                    v.append("")

        rows = []
        column_headers = []
        if times_by_hour_working_days and times_by_hour_weekend:
            column_headers.append("Рабочие дни")
            if has_sunday and has_saturday:
                column_headers.append("Выходные")
            elif has_sunday:
                column_headers.append("Суббота")
            elif has_saturday:
                column_headers.append("Воскресенье")
            rows.extend(
                [
                    {
                        "timesByHour": times_by_hour_working_days,
                    },
                    {
                        "timesByHour": times_by_hour_weekend,
                    },
                ]
            )
        else:
            column_headers.append("Ежедневно")
            column_headers.append("")
            rows.append(
                {
                    "timesByHour": times_by_hour_weekend,
                }
            )
            rows.append(
                {
                    "timesByHour": {},
                }
            )

        payload["head"]["shiftMinutes"] = stop_shift_in_minutes
        payload.update(
            {
                "body": {
                    "columnHeads": column_headers,
                    "rows": [
                        {
                            "name": "Рейсы",
                            "columns": rows,
                        }
                    ],
                },
            }
        )

    return payload
