#!/usr/bin/python
import json, sqlite3, sys, os, base64

from PIL import Image
import cStringIO

def main(args):

    if len(args) < 2:
        print("Incorrect number of command line arguments")
        sys.exit(2)

    cluster_name = args[0]
    output_file = args[1]

    fp = open(output_file, "wb")

    images = []

    for path in os.walk(cluster_name):
        image_name = path[0] + "/" + path[2][0]
        if path[2][0][0] != ".":
            print path[0] + "/" + path[2][0]

            with open(image_name, "rb") as f:
                image = Image.open(f)
                (w, h) = image.size

                image = image.resize((w / 2,h / 2), Image.ANTIALIAS)

                buffer = cStringIO.StringIO()
                image.save(buffer, format="JPEG")

                images.append({"name":path[2][0].replace(".jpg",""), "data": base64.b64encode(buffer.getvalue())})

    json_obj = []
    
    for image in images:
        json_obj.append({
            "data" : image["data"],
            "name" : image["name"]
        })

    fp.write(json.dumps(json_obj, sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    main(sys.argv[1:])
