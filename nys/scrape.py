import requests
from enum import Enum
import json
from datetime import datetime


class GovtLevel(Enum):
    STATE = 1
    COUNTY = 2


class Filer(Enum):
    ALL = 1
    CANDIDATE = 2
    COMMITTEE = 3


class Status(Enum):
    ALL = 1
    ACTIVE = 2
    TERMINATED = 3


class Registered(Enum):
    ALL = 1
    TODAY = 2
    LAST_7_DAYS = 3
    LAST_30_DAYS = 4
    LAST_YEAR = 5
    DATE_RANGE = 6


class Search:
    govt_level, filer, status, registered = None, None, None, None
    county_id, municipality_id = None, None

    county, municipality, date_range_data = "ALL", None, {}

    def __init__(self, govt_level: GovtLevel):
        self.govt_level = govt_level
        self.filer = Filer.ALL
        self.status = Status.ALL
        self.registered = Registered.ALL
        self.municipality = "ALL"

    def update(self, name, value, **kwargs):
        print("ran for {0}".format(name))
        if isinstance(value, Enum):
            setattr(self, name, value)
        else:
            if name == "registered":
                print(value)
                self.registered = Registered[value.replace(" ", "_").upper()]
                if self.registered == Registered.DATE_RANGE:
                    print("poooo")
            elif name == self.registered:
                print("ran")
                self.date_range_data[value] = kwargs.get('date')
            elif name == "filer":
                self.filer = Filer[value.replace(" ", "_").upper()]
            elif name == "status":
                self.status = Status[value.replace(" ", "_").upper()]
            else:
                setattr(self, name, value)


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
    return get(url)


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


def get_municipality(county_id):
    url = "https://publicreporting.elections.ny.gov/ActiveDeactiveFiler/GetMunicipality"
    payload = {
        "lstUCCounty": str(county_id)
    }
    return get(url, payload)


def get_filers(search: Search):
    url = "https://publicreporting.elections.ny.gov/ActiveDeactiveFiler/GetSearchListOfFilersData"
    headers = {
        "Accept": "application/json; charset=utf-8",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    }

    payload = {
        "lstOfficeType": str(search.govt_level.value),
        "lstCounty": "-+Select+-",
        "lstMunicipality": "-+Select+-",
        "lstStatus": search.status.name.capitalize(),
        "lstFilerType": "",  # needs to be removed and handled for ALL
        "lstOffice": "-+Select+-",
        "lstDistrict": "-+Select+-",
        "lstDateType": search.registered.name.capitalize().replace("_", "+"),
        "ddlCommitteeType": "-+Select+-",
        "txtDateFrom": "",
        "txtDateTo": ""
    }

    if search.filer != Filer.ALL:
        payload['lstFilerType'] = search.filer.name.capitalize()
    else:
        search.update('filer', Filer.CANDIDATE)
        f_1 = get_filers(search)
        search.update('filer', Filer.COMMITTEE)
        f_2 = get_filers(search)
        for item in f_2:
            f_1.append(item)
        return f_1

    if search.govt_level == GovtLevel.COUNTY:
        if search.county_id is not None:
            # this needs to pass a numerical value. get_counties returns an enum which has the values.
            payload['lstCounty'] = str(search.county_id)
            if search.municipality_id is not None:
                # this needs to pass a numerical value. get_municipalities returns a dict which has the values.
                payload['lstMunicipality'] = str(search.municipality_id)
            elif search.municipality.upper() == "ALL":
                payload['lstMunicipality'] = str(search.municipality).capitalize()
                # this shouldn't occur as the default value is ALL.
            else:
                print(search.municipality)
                raise ValueError("Select a municipality.")
    elif search.govt_level == GovtLevel.STATE:
        pass
    if search.registered == Registered.DATE_RANGE:
        if search.date_range_data is not None:
            # temporary, we should later prompt the user that they need to fix it.
            date = search.date_range_data
            if date['dateFrom'].strftime('%m/%d/%Y') > date['dateTo'].strftime('%m/%d/%Y'):
                payload['txtDateTo'] = date['dateFrom'].strftime('%m/%d/%Y')
                payload['txtDateFrom'] = date['dateTo'].strftime('%m/%d/%Y')
            else:
                payload['txtDateFrom'] = date['dateFrom'].strftime('%m/%d/%Y')
                payload['txtDateTo'] = date['dateTo'].strftime('%m/%d/%Y')
        else:
            # raise error saying that one of them is missing.
            pass

    print(payload)
    payload = "&".join([f"{key}={value}" for key, value in payload.items()]).replace(" ", "+")
    with requests.Session() as session:
        session.headers = headers
        rew = session.post(url, headers=headers, params=payload)
    return json.loads(rew.text)['aaData']




d = datetime(year=2010, month=8, day=1)
d_t = datetime(year=2020, month=8, day=1)
#print(get_filers(GovtLevel.STATE, Status.ACTIVE, d, d_t, Filer.CANDIDATE))
