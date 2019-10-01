"""Image filtering and processing utilities."""

import pathlib
import typing

import cv2
import numpy as np

import geometry_utils


def convert_to_grayscale(image: np.array) -> np.ndarray:
    """Convert an image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_hf_noise(image: np.array) -> np.ndarray:
    """Blur image slightly to remove high-frequency noise."""
    return cv2.GaussianBlur(image, (3, 3), 0)


def detect_edges(image: np.array) -> np.ndarray:
    """Detect edges in the image."""
    low_threshold = 100
    return cv2.Canny(image, low_threshold, low_threshold * 3, edges=3)


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


def convert_to_bw(image: np.array) -> np.ndarray:
    """Convert an image to B&W."""
    gray_image = convert_to_grayscale(image)
    _, image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return image


def get_fill_percent(image: np.array, polygon: geometry_utils.Polygon):
    """Get the percent of the pixels in the polygon that are not white."""
    contours = [geometry_utils.polygon_to_contour(polygon).astype(int)]
    cimg = np.zeros_like(image)
    cv2.drawContours(cimg, contours, -1, color=255, thickness=-1)
    pts = np.where(cimg == 255)
    intensities = image[pts[0], pts[1]]
    try:
        return (255 - (sum(intensities) / len(intensities))) / 255
    except ZeroDivisionError:
        return 0

