from math import radians, sin, cos, sqrt, atan2


def calculate_distance(point1, point2):
    """
    Calculate distance between two [longitude, latitude]
    points using the Haversine formula.

    Returns distance in meters.
    """

    lng1, lat1 = point1
    lng2, lat2 = point2

    R = 6371000  # Earth radius in meters

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lng / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def find_closest_route_point(point, route_coordinates):
    """
    Find the closest coordinate on the rider's route
    to the given passenger coordinate.

    Returns:
        {
            "closest_point": [...],
            "closest_distance": ...,
            "closest_index": ...
        }
    """

    closest_point = None
    closest_distance = float("inf")
    closest_index = -1

    for index, route_point in enumerate(route_coordinates):

        distance = calculate_distance(
            point,
            route_point,
        )

        if distance < closest_distance:
            closest_distance = distance
            closest_point = route_point
            closest_index = index

    return {
        "closest_point": closest_point,
        "closest_distance": closest_distance,
        "closest_index": closest_index,
    }


def is_intermediate_route(
    passenger_source,
    passenger_destination,
    route_coordinates,
    threshold=1000,
):
    """
    Check whether the passenger's journey is an
    intermediate section of the rider's route.
    """

    source_result = find_closest_route_point(
        passenger_source,
        route_coordinates,
    )

    destination_result = find_closest_route_point(
        passenger_destination,
        route_coordinates,
    )

    source_near_route = (
        source_result["closest_distance"] <= threshold
    )

    destination_near_route = (
        destination_result["closest_distance"] <= threshold
    )

    correct_order = (
        source_result["closest_index"]
        < destination_result["closest_index"]
    )

    is_match = (
        source_near_route
        and destination_near_route
        and correct_order
    )

    return {
        "is_match": is_match,
        "source_near_route": source_near_route,
        "destination_near_route": destination_near_route,
        "correct_order": correct_order,
        "source_result": source_result,
        "destination_result": destination_result,
    }