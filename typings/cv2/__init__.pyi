"""
Types for OpenCV.
"""

from numpy import ndarray
import typing


def imshow(title: str, image: ndarray):
    ...


def waitKey(key: int):
    ...


def imwrite(path: str, image: ndarray):
    ...


def cvtColor(image: ndarray, code: typing.Any) -> ndarray:
    ...


def GaussianBlur(image: ndarray, ksize: typing.Tuple[int, int],
                 sigmaX: float) -> ndarray:
    ...


def Canny(image: ndarray, threshold1: float, threshold2: float,
          L2gradient: bool, edges: int) -> ndarray:
    ...


def findContours(image: ndarray, mode: typing.Any,
                 method: typing.Any) -> typing.Any:
    ...


def imread(path: str) -> ndarray:
    ...


def threshold(image: ndarray, thresh: int, maxval: int,
              type: typing.Any) -> ndarray:
    ...


def dilate(image: ndarray, kernel: ndarray, iterations: int) -> ndarray:
    ...


def arcLength(a: ndarray, b: bool) -> float:
    ...


def approxPolyDP(a: ndarray, b: float, c: bool) -> ndarray:
    ...


def contourArea(a: ndarray, b: bool) -> ndarray:
    ...


def circle(img: ndarray, center: typing.Tuple[int, int], radius: int,
           color: typing.Tuple[int, int, int], thickness: int) -> ndarray:
    ...


THRESH_BINARY: int
THRESH_OTSU: int
CHAIN_APPROX_SIMPLE: int
RETR_TREE: int
COLOR_BGR2GRAY: int
