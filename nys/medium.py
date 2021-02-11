from enum import Enum

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


class Entity:
    govt_level, status, filer, registered = None, None, None, None
    name, address, id = None, None, None

    district, seat = None, None  # may be None at all times if Govt Level is Committee.

    committee_type = None  # may be None at all times if Govt Level is Candidate.

    def __init__(self, data_set, search: Search):
        self.govt_level = search.govt_level
        self.status = Status[data_set[13]]
        self.filer = Filer[data_set[1]]
        self.registered = data_set[11]

        self.name = data_set[5]
        self.address = data_set[10]
        self.id = data_set[4]

        if self.filer == Filer.CANDIDATE:
            self.district = data_set[7]
            self.seat = data_set[6]
        elif self.filer == Filer.COMMITTEE:
            self.committee_type = data_set[3]


