import functools
import json
import operator

from scipy import spatial

cluster_mapping = {}


@functools.lru_cache(maxsize=None)
def lowest_image(current_cluster_id):
    avg_images = {}

    assert isinstance(current_cluster_id, object)
    cluster = similarity_mapping[current_cluster_id]

    for image in cluster:
        images = cluster[image].values()
        avg_images[image] = sum(images) / len(cluster[image])

    return feature_vectors[min(avg_images.items(), key=operator.itemgetter(1))[0]]


def compute_similarity_clusters(current_cluster_id, current_comparing_cluster_id):
    return 1 - spatial.distance.cosine(lowest_image(current_cluster_id), lowest_image(current_comparing_cluster_id))


with open("similarity-mapping.json", "r") as similarity_mapping_file, open("processed-formal-feature-vectors.txt",
                                                                           "r") as feature_vectors_file:
    print("Loading similarity mapping file...")
    similarity_mapping = json.loads(similarity_mapping_file.read())
    print("Loading feature vectors...")
    feature_vectors_json = json.loads(feature_vectors_file.read())
    feature_vectors = {}

    print("Processing feature vectors... ")
    for image_path in feature_vectors_json.keys():
        image_id = image_path.split("/")[-1]
        vector = feature_vectors_json[image_path]

        feature_vectors[image_id] = vector

    num_clusters = len(similarity_mapping.keys())
    count = 0
    print("Calculating intra-cluster similarities")
    for cluster_id in similarity_mapping.keys():
        cluster_mapping[cluster_id] = {}

        for comparing_cluster_id in similarity_mapping.keys():
            similarity = compute_similarity_clusters(comparing_cluster_id, cluster_id)

            if similarity > 0.86:
                cluster_mapping[cluster_id][comparing_cluster_id] = similarity

        count += 1
        print(str(count) + "/" + str(num_clusters))

with open("cluster_similarity_mapping.json", "w") as cluster_similarity_mapping_file:
    cluster_similarity_mapping_file.write(json.dumps(cluster_mapping))
