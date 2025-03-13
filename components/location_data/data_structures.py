import json
from dataclasses import dataclass

@dataclass
class Location:
    x: float
    y: float
    z: float = None
    width: float = None
    height: float = None
    yaw: float = None
    pitch: float = None
    roll: float = None
    id_num: int = None

@dataclass
class Status:
    enabled: bool
    healthy: bool
    framerate: float

def jsonToLocation(data):
    """
    parses a stringified list of location data objects to a list of location dataclass
    """
    data = json.loads(data)
    output = []
    for i in data:
        location = Location(i["x"],\
          i["z"],\
          i["y"],\
          i["width"],\
          i["height"],\
          i["yaw"],\
          i["pitch"],\
          i["roll"],\
          i["id"])
        output.append(location)
    output
    return output

def jsonToStatus(data):
    """
    parses a status object string to a status dataclass
    """
    data = json.loads(data)
    output = Status(data["enabled"],\
        data["healthy"],\
        data["framerate"])
    return output