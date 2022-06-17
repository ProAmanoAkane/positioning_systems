from dataclasses import dataclass


@dataclass
class NormalizedHistogram:
    mac_address: str
    rssi: float