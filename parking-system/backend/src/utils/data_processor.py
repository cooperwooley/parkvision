import json
from collections import defaultdict

TOLERANCE = 5


"""
    Normalize spot information. Same bounding area and more ideal (x,y) positioning

    Args:
        spots (list): list parking spot infomation

    Returns:
        list: list of normalized parking spot information
"""
def normalize(spots):
    # Calculate average width and height
    avg_width = round(sum(spot["width"] for spot in spots) / len(spots))
    avg_height = round(sum(spot["height"] for spot in spots) / len(spots))

    # Cluster x and y coordinates to find ideal positions
    x_coords = defaultdict(list)
    y_coords = defaultdict(list)
    for spot in spots:
        x_coords[spot["x"]].append(spot)
        y_coords[spot["y"]].append(spot)

    # Define normalized x and y values based on clusters
    x_normalized = {}
    y_normalized = {}
    for x in sorted(x_coords.keys()):
        if not x_normalized:
            x_normalized[x] = x
        else:
            closest = min(x_normalized.keys(), key=lambda k: abs(k - x))
            if abs(x - closest) <= TOLERANCE:
                x_normalized[x] = x_normalized[closest]
            else:
                x_normalized[x] = x
    
    for y in sorted(y_coords.keys()):
        if not y_normalized:
            y_normalized[y] = y
        else:
            closest = min(y_normalized.keys(), key=lambda k: abs(k - y))
            if abs(y - closest) <= TOLERANCE:
                y_normalized[y] = y_normalized[closest]
            else:
                y_normalized[y] = y

    # Update spots with normalized values
    for spot in spots:
        spot["width"] = avg_width
        spot["height"] = avg_height
        spot["x"] = x_normalized[spot["x"]]
        spot["y"] = y_normalized[spot["y"]]

    # Output the normalized JSON
    return spots