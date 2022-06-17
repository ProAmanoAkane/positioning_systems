import utils
from flask import Flask, request
from systems import *


def main():
    data = utils.import_csv('src/data/data.csv')
    samples = get_samples(data=data)
    database = gen_database(samples=samples)


    create_fingerprint_table = f"CREATE TABLE fingerprint_value(id integer primary key, loc_id integer not null, ap_id integer not null, foreign key(ap_id) references accesspoint(id), foreign key(loc_id) references location(id));"
    create_calibrating_mobile_table = f"CREATE TABLE calibrating_mobile(mac_address text primary key, loc_id integer not null, foreign key(loc_id) references location(id));"

    utils.sqlite_request("src/rssi.db", create_fingerprint_table)
    utils.sqlite_request("src/rssi.db", create_calibrating_mobile_table)

    app = Flask(__name__)

    @app.route('/')
    def index():
        return "200 OK"
    
    @app.route('/rssi', methods = ['GET'])
    def put_rssi():
        mac_address = request.args.get('mac', None)
        rssi = request.args.get('rssi', None)
        res = RSSISample(mac_address=str(mac_address), rssi=float(rssi))
        return f"{res.mac_address}:{res.rssi}"

    app.run(debug=True)

if __name__ == '__main__':
    main()