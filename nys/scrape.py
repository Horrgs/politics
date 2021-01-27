import requests
from enum import Enum
import json
from datetime import datetime


class GovtLevel(Enum):
    STATE = 1
    COUNTY = 2


class Filer(Enum):
    CANDIDATE = 1
    COMMITTEE = 2


class Status(Enum):
    ACTIVE = 1
    TERMINATED = 2


def get(url, payload=None):
    if payload is not None:
        req = requests.post(url, data=payload)
    else:
        req = requests.post(url)
    response = {}
    for item in json.loads(req.text):
        response[item['Text']] = int(item['Value'])
    response = dict(sorted(response.items(), key=lambda obj: obj[1]))
    return response


def get_counties():
    url = "https://publicreporting.elections.ny.gov/ActiveDeactiveFiler/GetCounty"
    return Enum('County', get(url))


def get_offices(govt_level: GovtLevel):
    url = "https://publicreporting.elections.ny.gov/ActiveDeactiveFiler/GetOffice"
    payload = {
        "lstUCOfficeType": str(govt_level.value),
        "lstUCCounty": "",
        "lstUCMuncipality": ""
    }
    print(get(url, payload))
    return Enum('Office', get(url, payload))


def get_committees():
    url = "https://publicreporting.elections.ny.gov/ActiveDeactiveFiler/GetCommitteeType"
    return Enum('Committee', get(url))


def get_filers(govt_level: GovtLevel, status: Status, date_from, date_to, filer_type: Filer, **kwargs):
    url = "https://publicreporting.elections.ny.gov/ActiveDeactiveFiler/GetSearchListOfFilersData"
    headers = {
        "Accept": "application/json; charset=utf-8",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    }

    payload = {
        "lstOfficeType": str(govt_level.value),
        "lstCounty": "-+Select+-",
        "lstMunicipality": "-+Select+-",
        "lstStatus": status.name,
        "lstFilerType": filer_type.name,
        "lstOffice": "-+Select+-",
        "lstDistrict": "-+Select+-",
        "lstDateType": "Date+Range",
        "ddlCommitteeType": "-+Select+-",
        "txtDateFrom": date_from.strftime('%m/%d/%Y'),
        "txtDateTo": date_to.strftime('%m/%d/%Y')
    }

    if govt_level == GovtLevel.COUNTY:
        if kwargs.get('county') is not None:
            if kwargs.get('municipality') is not None:
                payload['lstCounty'] = kwargs.get('county')
                payload['lstMunicipality'] = kwargs.get('municipality')
            else:
                # this shouldn't occur as the default value is ALL.
                raise ValueError("Select a municipality.")
        else:
            # this shouldn't occur as the default value is ALL.
            raise ValueError("Select a county.")

    payload = "&".join([f"{key}={value}" for key, value in payload.items()]).replace(" ", "+")
    with requests.Session() as session:
        session.headers = headers
        rew = session.post(url, headers=headers, params=payload)
    return json.loads(rew.text)


d = datetime(year=2010, month=8, day=1)
d_t = datetime(year=2020, month=8, day=1)
print(get_filers(GovtLevel.STATE, Status.ACTIVE, d, d_t, Filer.CANDIDATE))
