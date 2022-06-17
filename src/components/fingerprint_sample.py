from dataclasses import dataclass


@dataclass
class FingerprintSample:
    mac_address: str
    average: float