"""Image filtering and processing utilities."""

import math
import pathlib
import typing

import cv2
import numpy as np

import geometry_utils

SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"]


def convert_to_grayscale(image: np.array) -> np.ndarray:
    """Convert an image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_hf_noise(image: np.array) -> np.ndarray:
    """Blur image slightly to remove high-frequency noise."""
    return cv2.GaussianBlur(image, (0, 0), sigmaX=math.sqrt(2))


def detect_edges(image: np.array) -> np.ndarray:
    """Detect edges in the image."""
    low_threshold = 100
    return cv2.Canny(image,
                     low_threshold,
                     low_threshold * 3,
                     L2gradient=True,
                     edges=3)


def find_contours(edges: np.array) -> np.ndarray:
    """Find the contours in an edge-detected image."""
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)
    return contours


def get_image(path: pathlib.PurePath) -> np.array:
    """Returns the cv2 image located at the given path."""
    return cv2.imread(str(path))


def find_polygons(image: np.array) -> typing.List[geometry_utils.Polygon]:
    """Returns a list of polygons found in the image."""
    edges = detect_edges(image)
    all_contours = find_contours(edges)
    polygons = [
        geometry_utils.approx_poly(contour) for contour in all_contours
    ]
    return polygons


def get_dimensions(image: np.array) -> typing.Tuple[int, int]:
    """Returns the dimensions of the image in `(width, height)` form."""
    height, width, _ = image.shape
    return width, height


def threshold(image: np.array) -> np.ndarray:
    """Convert an image to B&W by thresholding."""
    gray_image = convert_to_grayscale(image)
    _, result = cv2.threshold(gray_image, 128, 255,
                              cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return result


def prepare_scan_for_processing(image: np.array) -> np.array:
    return threshold(remove_hf_noise(image))


def get_fill_percent(image: np.array, top_left_point: geometry_utils.Point,
                     bottom_right_point: geometry_utils.Point) -> float:
    """Get the percent of the pixels in the range that are not white."""
    # +1 because indexing doesn't include the last number (ie, [1,2,3,4][1:3] ->
    # [2,3]) and we want that last row / column.
    x_range = (int(top_left_point.x), int(bottom_right_point.x) + 1)
    y_range = (int(top_left_point.y), int(bottom_right_point.y) + 1)
    image_section = image[y_range[0]:y_range[1], x_range[0]:x_range[1]]
    try:
        return 1 - (np.mean(image_section) / 255)
    except ZeroDivisionError:
        return 0


def dilate(image: np.array) -> np.array:
    return cv2.dilate(image, np.ones((3, 3), np.uint8), iterations=1)
