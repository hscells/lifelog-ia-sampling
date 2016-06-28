#!/usr/bin/python

import json
from scipy import spatial

feature_vectors = {}
similarity_mapping = {}

with open("image_cluster_mapping.json", "r") as image_cluster_mapping_file:
    print "Loading cluster mapping..."
    image_cluster_mapping = json.loads(image_cluster_mapping_file.read())

    with open("processed-formal-feature-vectors.txt", "r") as feature_vectors_file:
        print "Loading feature vectors..."
        feature_vectors_json = json.loads(feature_vectors_file.read())

        print "Processing feature vectors... "
        for image_path in feature_vectors_json.keys():
            image_id = image_path.split("/")[-1]
            vector = feature_vectors_json[image_path]

            feature_vectors[image_id] = vector

        num_clusters = len(image_cluster_mapping.keys())
        print "Calculating similarity for inter-cluster images..."
        for cluster_id in image_cluster_mapping:
            similarity_mapping[cluster_id] = {}

            for image_id in image_cluster_mapping[cluster_id]:
                feature_vector = feature_vectors[image_id]

                similarity_mapping[cluster_id][image_id] = {}

                for comparing_image_id in image_cluster_mapping[cluster_id]:
                    comparing_feature_vector = feature_vectors[comparing_image_id]

                    similarity = 1 - spatial.distance.cosine(feature_vector, comparing_feature_vector)

                    similarity_mapping[cluster_id][image_id][comparing_image_id] = similarity

            print str(len(similarity_mapping.keys())) + "/" + str(num_clusters) + " - " + str(cluster_id)

with open("similarity-mapping.json", "w") as similarity_mapping_file:
    similarity_mapping_file.write(json.dumps(similarity_mapping))
