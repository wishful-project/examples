import math


def build_centroids(data, radius=0.1):
    centroids = []
    pointsNum = len(data)
    inputData = [None for y in range(pointsNum)]
    clusters_center = [0.0 for y in range(pointsNum)]
    matrix_d = [None for x in range(pointsNum)]
    for i in range(0, pointsNum):
        inputData[i] = data[i]
    # First cluster
    a = pow(4.0/radius, 2)
    dinami = 0.0
    for i in range(pointsNum):
        summary = 0.0
        for j in range(pointsNum):
            if i!=j:
                distance = math.sqrt(pow(inputData[i] - inputData[j], 2.0))
                dinami = distance * a
                summary  += pow(math.exp(1), -dinami)
        matrix_d[i] = summary
    port_val = matrix_d[0]
    index = 0
    for i in range(1, pointsNum):
        if matrix_d[i]>port_val:
            port_val = matrix_d[i]
            index = i
    first_port_val = port_val
    previous_cluster_pot = port_val
    current_cluster = 0
    clusters_center[current_cluster] = inputData[index]
    matrix_d[index] = 0.0
    current_cluster += 1
    centroids.append(inputData[index])
    # Next cluster
    while 1:
        for i in range(pointsNum):
            distance = math.sqrt(pow(inputData[i] - clusters_center[current_cluster-1], 2.0))
            dinami = 4.0* distance / pow(1.25*radius, 2)
            matrix_d[i] = matrix_d[i] - first_port_val * pow(math.exp(1), -dinami)
        found = False
        counter = 0
        while not found:
            port_val = matrix_d[0]
            index = 0
            for i in range(1, pointsNum):
                if matrix_d[i] > port_val:
                    port_val = matrix_d[i]
                    index = i
            dMin = 99999.0
            for i in range(0, current_cluster):
                if math.sqrt(pow(inputData[index]-clusters_center[i], 2.0)) < dMin:
                    dMin = math.sqrt(pow(inputData[index]-clusters_center[i], 2.0))
            if (dMin / radius) + (port_val / previous_cluster_pot) >= 1.0:
                found = True
                clusters_center[current_cluster] = inputData[index]
                previous_cluster_pot = port_val
                matrix_d[index] = 0.0
                current_cluster += 1
                centroids.append(inputData[index])
            else:
                matrix_d[index] = 0.0
            counter += 1
            if counter == pointsNum:
                break
        if port_val < (0.5 * first_port_val):
            return centroids;


def value_belongs_to_centroid_with_index(value, index, centroids):
    measurement_centroid = centroids[index]
    minimum = math.sqrt(math.pow(value-measurement_centroid, 2))
    for other_centroid in [s for s in centroids if s!=centroids[index]]:
        distance = math.sqrt(math.pow(other_centroid-value, 2))
        if distance < minimum:
            return False
    return True



def check_centroids_status(centroids, initial_measurements, threashold):
    affected_values = []
    for index in range(len(centroids)):
        if centroids[index] > threashold:
            for measument in initial_measurements:
                if value_belongs_to_centroid_with_index(measument["value"], index, centroids):
                    affected_values.append(measument)
    return affected_values
