from dataclasses import dataclass
from components.location import Location


@dataclass
class AccessPoint:
    mac_address: str
    localtion: Location
    output_power_dBm: float = 20.0
    antenna_power_dBi: float = 5.0
    output_frequency_hz: float = 2417000000
