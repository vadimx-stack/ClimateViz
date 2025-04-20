import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "demo"
BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"


def fetch_stations(limit=1000, offset=1):
    url = f"{BASE_URL}stations"
    headers = {"token": API_KEY}
    params = {
        "limit": limit,
        "offset": offset
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Ошибка API: {response.status_code}"}


def fetch_data_types(limit=1000, offset=1):
    url = f"{BASE_URL}datatypes"
    headers = {"token": API_KEY}
    params = {
        "limit": limit,
        "offset": offset
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Ошибка API: {response.status_code}"}


def fetch_location_categories(limit=1000, offset=1):
    url = f"{BASE_URL}locationcategories"
    headers = {"token": API_KEY}
    params = {
        "limit": limit,
        "offset": offset
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Ошибка API: {response.status_code}"}


def fetch_locations(location_category=None, limit=1000, offset=1):
    url = f"{BASE_URL}locations"
    headers = {"token": API_KEY}
    params = {
        "limit": limit,
        "offset": offset
    }
    
    if location_category:
        params["locationcategoryid"] = location_category
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Ошибка API: {response.status_code}"}


def fetch_data(datasetid, startdate, enddate, locationid=None, stationid=None, datatypeid=None, limit=1000):
    url = f"{BASE_URL}data"
    headers = {"token": API_KEY}
    
    if isinstance(startdate, datetime):
        startdate = startdate.strftime("%Y-%m-%d")
    
    if isinstance(enddate, datetime):
        enddate = enddate.strftime("%Y-%m-%d")
    
    params = {
        "datasetid": datasetid,
        "startdate": startdate,
        "enddate": enddate,
        "limit": limit
    }
    
    if locationid:
        params["locationid"] = locationid
    
    if stationid:
        params["stationid"] = stationid
    
    if datatypeid:
        params["datatypeid"] = datatypeid
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            df = pd.DataFrame(data["results"])
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            return df
        return pd.DataFrame()
    else:
        print(f"Ошибка API: {response.status_code}")
        return pd.DataFrame()


def get_demo_temperature_data():
    start_date = datetime.now() - timedelta(days=365*5)
    end_date = datetime.now()
    
    return fetch_data(
        datasetid="GHCND",
        startdate=start_date,
        enddate=end_date,
        datatypeid="TAVG",
        locationid="CITY:US000001",
        limit=1000
    )


def get_sample_data():
    dates = pd.date_range(start=datetime.now() - timedelta(days=365*5), end=datetime.now(), freq='M')
    
    temperature_data = pd.DataFrame({
        'date': dates,
        'value': [20 + 5 * i/len(dates) + 10 * (0.5 - 0.5 * ((i % 12) - 6)/6) + 2 * (0.5 - (i % 2)) for i in range(len(dates))],
        'type': 'TAVG'
    })
    
    precipitation_data = pd.DataFrame({
        'date': dates,
        'value': [50 + 30 * ((i % 12) - 6)/6 + 10 * ((i % 3) - 1)/1 for i in range(len(dates))],
        'type': 'PRCP'
    })
    
    extreme_events = pd.DataFrame({
        'date': pd.date_range(start=datetime.now() - timedelta(days=365*5), end=datetime.now(), freq='120D'),
        'value': [90 + i * 2 for i in range(15)],
        'type': 'EXTREME'
    })
    
    return pd.concat([temperature_data, precipitation_data, extreme_events]) 