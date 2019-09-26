"""Image filtering and processing utilities."""

import pathlib
import typing

import cv2
import numpy as np

from . import geometry_utils


def convert_to_grayscale(image: np.array) -> np.array:
    """Convert an image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_hf_noise(image: np.array) -> np.array:
    """Blur image slightly to remove high-frequency noise."""
    return cv2.GaussianBlur(image, (3, 3), 0)


def detect_edges(image: np.array) -> np.array:
    """Detect edges in the image."""
    low_threshold = 100
    return cv2.Canny(image, low_threshold, low_threshold * 3, edges=3)


def find_contours(edges: np.array):
    """Find the contours in an edge-detected image."""
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)
    return contours


def get_image(path: pathlib.PurePath) -> np.array:
    """Returns the cv2 image located at the given path."""
    return cv2.imread(str(path))


def find_polygons(image: np.array):
    """Returns a list of polygons found in the image."""
    processed_image = remove_hf_noise(convert_to_grayscale(image))
    edges = detect_edges(processed_image)
    all_contours = find_contours(edges)
    polygons = [
        geometry_utils.approx_poly(contour) for contour in all_contours
    ]
    return polygons


def get_dimensions(image: np.array) -> typing.Tuple[int, int]:
    """Returns the dimensions of the image in `(width, height)` form."""
    height, width, _ = image.shape
    return width, height
