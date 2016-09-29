#!/usr/bin/python

import json
import pg8000
import argparse
import os
import sys


def import_json(json_file):
    if os.environ.get("LIFELOG_DB_USER") is None or \
                    os.environ.get("LIFELOG_DB_PASS") is None or \
                    os.environ.get("LIFELOG_DB_HOST") is None or \
                    os.environ.get("LIFELOG_DB_NAME") is None:
        print("Environment variables are not set!")
        sys.exit(1)

    print("Connecting...")
    json_data = json.load(open(json_file))
    conn = pg8000.connect(user=os.environ.get("LIFELOG_DB_USER"),
                          password=os.environ.get("LIFELOG_DB_PASS"),
                          host=os.environ.get("LIFELOG_DB_HOST"),
                          database=os.environ.get("LIFELOG_DB_NAME"))
    cursor = conn.cursor()

    print("Rebuilding tables...")
    sql = open("database.sql", "r").read()
    cursor.execute(sql)
    conn.commit()

    print("Inserting data...")

    for item in json_data:
        row = [item["name"], item["data"]]
        cursor.execute('INSERT INTO images (name, data) VALUES (%s, %s)', row)
    conn.commit()
    cursor.close()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Import JSON into sqlite')
    argparser.add_argument('json_file', help='The JSON file to import.')
    args = argparser.parse_args()

    import_json(args.json_file)
