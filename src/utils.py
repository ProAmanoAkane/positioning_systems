import csv
import sqlite3

def import_csv(filepath: str):
    """
        Imports a csv file
        :param filepath: path to the csv file
    """
    with open(filepath, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        data = list(reader)
        return data

def sqlite_request(filepath: str, statement: str) -> None:
    connector = sqlite3.connect(filepath)
    cursor = connector.cursor()
    print("connected")

    try:
        cursor.execute(statement)
        print("statement executed")
        connector.commit()
        connector.close()

    except sqlite3.OperationalError as e:
        print(e)
    
    finally:
        if connector:
            connector.close()
            print("connection closed")
    
    print("connection closed")