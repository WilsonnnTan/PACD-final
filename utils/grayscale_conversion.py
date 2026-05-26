from __future__ import annotations

from typing import Any, TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

RGBPixel: TypeAlias = tuple[int, int, int]
GrayscalePixel: TypeAlias = int

__all__ = ["rgb_to_grayscale_average_conversion"]


def rgb_to_grayscale_average_conversion(img_object: PILImage) -> PILImage:
    """Convert every RGB pixel into grayscale using the average method."""
    rgb_image = img_object.convert("RGB")
    _, width, height, source_pixels = _image_copy(rgb_image)
    grayscale_img = Image.new("L", (width, height))
    grayscale_pixels = grayscale_img.load()
    if grayscale_pixels is None:
        raise ValueError("Unable to access pixel data from the grayscale image.")

    for y in range(height):
        for x in range(width):
            pixel = source_pixels[x, y]
            grayscale_pixels[x, y] = _average_rgb_channels(pixel)

    return grayscale_img


def _image_copy(img_object: PILImage) -> tuple[PILImage, int, int, Any]:
    """Create a copy of the RGB source image and expose its pixel access object."""
    img_object_copy = img_object.copy()
    width, height = img_object_copy.size
    pixels = img_object_copy.load()
    if pixels is None:
        raise ValueError("Unable to access pixel data from the source image copy.")
    return img_object_copy, width, height, pixels


def _average_rgb_channels(pixel: RGBPixel) -> GrayscalePixel:
    """Compute the grayscale value by averaging the three RGB channels."""
    r, g, b = pixel
    return round((r + g + b) / 3)
