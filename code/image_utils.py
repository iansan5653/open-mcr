"""Image filtering and processing utilities."""

import pathlib
import typing

import cv2
import numpy as np
from numpy import ma

import geometry_utils

SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"]


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def remove_hf_noise(image: np.ndarray) -> np.ndarray:
    """Blur image slightly to remove high-frequency noise."""
    # This value for sigma was chosen such that sigma=sqrt(2) for 2500px images.
    # Still needs more verification for low-res images.
    sigma = min(get_dimensions(image)) * (5.6569e-4)
    result = cv2.GaussianBlur(image, (0, 0), sigmaX=sigma)
    return result


def detect_edges(image: np.ndarray) -> np.ndarray:
    """Detect edges in the image."""
    low_threshold = 100
    return cv2.Canny(image,
                     low_threshold,
                     low_threshold * 3,
                     L2gradient=True,
                     edges=3)


def find_contours(edges: np.ndarray) -> np.ndarray:
    """Find the contours in an edge-detected image."""
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)
    return contours


def get_image(path: pathlib.PurePath) -> np.ndarray:
    """Returns the cv2 image located at the given path."""
    return cv2.imread(str(path))


def find_polygons(image: np.ndarray) -> typing.List[geometry_utils.Polygon]:
    """Returns a list of polygons found in the image."""
    edges = detect_edges(image)
    all_contours = find_contours(edges)
    polygons = [
        geometry_utils.approx_poly(contour) for contour in all_contours
    ]
    return polygons


def get_dimensions(image: np.ndarray) -> typing.Tuple[int, int]:
    """Returns the dimensions of the image in `(width, height)` form."""
    height, width, _ = image.shape
    return width, height


def threshold(image: np.ndarray) -> np.ndarray:
    """Convert an image to B&W by thresholding."""
    gray_image = convert_to_grayscale(image)
    _, result = cv2.threshold(gray_image, 128, 255,
                              cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return result


def prepare_scan_for_processing(image: np.ndarray) -> np.ndarray:
    return threshold(remove_hf_noise(image))


def get_fill_percent(matrix: typing.Union[np.ndarray, ma.MaskedArray]) -> float:
    """Get the percent of the pixels in the B&W matrix that are not white."""
    try:
        return 1 - (matrix.mean() / 255)
    except ZeroDivisionError:
        return 0


def dilate(image: np.ndarray) -> np.ndarray:
    return cv2.dilate(image, np.ones((3, 3), np.uint8), iterations=1)
