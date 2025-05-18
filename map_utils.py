def calculate_spn(toponym):
    envelope = toponym["boundedBy"]["Envelope"]
    lower_corner = envelope["lowerCorner"].split()
    upper_corner = envelope["upperCorner"].split()

    width = abs(float(upper_corner[0]) - float(lower_corner[0]))
    height = abs(float(upper_corner[1]) - float(lower_corner[1]))

    return f"{width},{height}"


def calculate_bbox(points):
    lons = [float(p[0]) for p in points]
    lats = [float(p[1]) for p in points]

    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    return f"{min_lon},{min_lat}~{max_lon},{max_lat}"
