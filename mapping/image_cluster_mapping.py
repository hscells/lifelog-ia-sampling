#!/usr/bin/python
import json, sqlite3, sys, os, base64

from PIL import Image
import cStringIO

def main(args):

    if len(args) < 2:
        print("Incorrect number of command line arguments")
        sys.exit(2)

    cluster_folder_name = args[0]
    output_file = args[1]

    fp = open(output_file, "wb")

    images = {}

    for path in os.walk(cluster_folder_name):
        cluster_name = path[0].split("/")[-1]
        if cluster_name not in images.keys():
            images[cluster_name] = []

        print path[-1]
        for image_name in path[-1]:



            images[cluster_name].append(image_name)

    fp.write(json.dumps(images, sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    main(sys.argv[1:])
