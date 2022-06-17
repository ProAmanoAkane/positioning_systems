from dataclasses import dataclass


@dataclass
class RSSISample:
    mac_address: str
    rssi: float
