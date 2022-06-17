from math import log10, pi
from components.rssi_sample import RSSISample
from components.fingerprint_sample import FingerprintSample
from components.database import Database
from components.access_point import AccessPoint
from components.location import Location


def simple_matching(rssi_sample: RSSISample, database: Database) -> Location:
    """
        Function simple_matching computes the location of a device based on the RSSISample and the database of fingerprint samples.
        :param rssi_sample: the RSSISample of the device
        :param database: the database of fingerprint samples
        :return: the location of the device
    """
    # create a dictionary of distances
    distances = {}
    for sample in database.data:
        distances[sample.mac_address] = compute_distance(rssi_sample, sample)

    # compute the location
    return multilateration(distances, database.access_points)


# create a function that computes de distance between two RSSISamples
def compute_distance(rssi_sample_1: RSSISample, rssi_sample_2: RSSISample) -> float:
    """
        Function compute_distance computes the distance between two RSSISamples.
        :param rssi_sample_1: the first RSSISample
        :param rssi_sample_2: the second RSSISample
        :return: the distance (meters)
    """
    # compute the average RSSI
    average_rssi = (rssi_sample_1.rssi + rssi_sample_2.rssi)/2

    # compute the distance
    distance = pow(10, (average_rssi-rssi_sample_1.rssi)/10)

    return distance

def multilateration(distances: dict, ap_locations: dict) -> Location:
    """
        Function compute_location computes a location based on the distance to some access points.
        :param distances: the distance between the access point and the device
        :param ap_locations: the location of the access points
        :return: the location of the device
    """
    # compute the average RSSI for each access point
    average_rssi = {}
    for key in distances:
        average_rssi[key] = __get_average_rssi__(distances[key])

    # compute the FBCM index for each access point
    fbcm_index = {}
    for key in ap_locations:
        fbcm_index[key] = compute_FBCM_index(distances[key], RSSISample(average_rssi[key]), ap_locations[key])

    # compute the estimated distance for each access point
    estimated_distances = {}
    for key in ap_locations:
        estimated_distances[key] = compute_estimated_distance(average_rssi[key], fbcm_index[key], ap_locations[key])

    # compute the location
    x = 0
    y = 0
    z = 0
    for key in ap_locations:
        x += ap_locations[key].x * estimated_distances[key]
        y += ap_locations[key].y * estimated_distances[key]
        z += ap_locations[key].z * estimated_distances[key]
    return Location(x, y, z)



def compute_FBCM_index(distance: float, rssi_values: RSSISample, access_point: AccessPoint) -> float:
    """
        Function compute_FBCM_index computes a FBCM index based on the distance (between transmitter and receiver)
        and the AP parameters. We consider the mobile device's antenna gain is 2.1 dBi.
        :param distance: the distance between AP and device
        :param rssi_values: the RSSI values associated to the AP for current calibration point. Use their average value.
        :return: one value for the FBCM index
    """

    transmitted_power = access_point.output_power_dBm
    transmitted_gain = access_point.antenna_power_dBi
    received_power = rssi_values.rssi
    received_gain = 2.1

    frequency = access_point.output_frequency_hz

    index = (received_power-transmitted_power-received_gain-transmitted_gain)/(10*log10(300000/(frequency*1000*4*pi*distance)))

    return index

def compute_estimated_distance(rssi_avg: float, fbcm_index: float, access_point: AccessPoint) -> float:
    """
        Function estimate_distance estimates the distance between an access point and a test point based on
        the test point rssi sample.
        :param rssi: average RSSI value for test point
        :param fbcm_index: index to use
        :param ap: access points parameters used in FBCM
        :return: the distance (meters)
    """
    distance = 0
    transmitted_power = access_point.output_power_dBm
    transmitted_gain = access_point.antenna_power_dBi
    received_power = rssi_avg
    received_gain = 2.1

    frequency = access_point.output_frequency_hz

    index = fbcm_index

    distance = pow(10,
        (transmitted_power-received_power+transmitted_gain+received_gain+20*log10(300000/frequency*4*pi))/10*index
    )

    return distance


def __get_average_rssi__(values: float) -> float:
    values_mw = []
    # convert from dBm to Mw
    for value in values:
        power_in_mW = 10**(value/10.)
        values_mw.append(power_in_mW)

    # average the values
    average_mW = sum(values_mw)/len(values_mw)

    # convert back to dBm
    average_dBm = 10. * log10(average_mW)
    
    # round average to 2 decimals
    average_dBm = round(average_dBm, 2)
    return average_dBm

def get_access_points():
    return {
            "00:13:ce:95:e1:6f": AccessPoint(
                mac_address="00:13:ce:95:e1:6f",
                localtion=Location(4.93, 25.81, 3.55)
            ),
            "00:13:ce:95:de:7e": AccessPoint(
                mac_address="00:13:ce:95:de:7e",
                localtion=Location(4.83, 10.88, 3.78)
            ),
            "00:13:ce:97:78:79": AccessPoint(
                mac_address="00:13:ce:97:78:79",
                localtion=Location(20.05, 28.31, 3.74)
            ),
            "00:13:ce:8f:77:43": AccessPoint(
                mac_address="00:13:ce:8f:77:43",
                localtion=Location(4.13, 7.085, 0.80)
            ),
            "00:13:ce:8f:78:d9": AccessPoint(
                mac_address="00:13:ce:8f:78:d9",
                localtion=Location(5.74, 30.35, 2.04)
            )
        }

def gen_database(samples: dict):
    db = Database()
    for key in samples:
        values = [float(value) for value in samples[key]]
        db.data.append(FingerprintSample(
            mac_address=key,
            average=__get_average_rssi__(values)
        ))
    
    return db

def get_samples(data: list):
    samples = {}
    for index, row in enumerate(data):
        start = 4
        end = len(data[index])
        step = 2
        for row in range(start, end, step):
            mac_address = data[index][row]
            rssi = data[index][row+1]
            if  samples.get(mac_address):
                values = samples[mac_address]
                values.append(rssi)
                samples[mac_address] = values
            else:
                samples[mac_address] = [rssi]
    return samples
