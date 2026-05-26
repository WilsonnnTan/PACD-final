from __future__ import annotations

from typing import Any, TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

RGBPixel: TypeAlias = tuple[int, int, int]
RGBFloatPixel: TypeAlias = tuple[float, float, float]
HSVPixel: TypeAlias = tuple[float, float, float]
HSVEncodedPixel: TypeAlias = tuple[int, int, int]

__all__ = ["rgb_to_hsv_conversion"]


def rgb_to_hsv_conversion(img_object: PILImage) -> PILImage:
    """Convert every RGB pixel into Pillow's 8-bit HSV representation."""
    rgb_image = img_object.convert("RGB")
    _, width, height, source_pixels = _image_copy(rgb_image)
    hsv_img = Image.new("HSV", (width, height))
    hsv_pixels = hsv_img.load()
    if hsv_pixels is None:
        raise ValueError("Unable to access pixel data from the HSV image.")

    for y in range(height):
        for x in range(width):
            pixel = source_pixels[x, y]
            normalized = _normalization(pixel)
            hsv_pixel = _rgb_to_hsv(normalized)
            hsv_pixels[x, y] = _encode_hsv_pixel(hsv_pixel)

    return hsv_img


def _image_copy(img_object: PILImage) -> tuple[PILImage, int, int, Any]:
    """Create a copy of the RGB source image and expose its pixel access object."""
    img_object_copy = img_object.copy()
    width, height = img_object_copy.size
    pixels = img_object_copy.load()
    if pixels is None:
        raise ValueError("Unable to access pixel data from the source image copy.")
    return img_object_copy, width, height, pixels


def _normalization(pixel: RGBPixel) -> RGBFloatPixel:
    """Scale 8-bit RGB channel values into the normalized range [0, 1]."""
    r, g, b = pixel
    return (r / 255.0, g / 255.0, b / 255.0)


def _rgb_to_hsv(pixel: RGBFloatPixel) -> HSVPixel:
    """Convert normalized RGB values into HSV values."""
    r, g, b = pixel
    max_value = max(r, g, b)
    min_value = min(r, g, b)
    delta = max_value - min_value

    if delta == 0:
        hue = 0.0
    elif max_value == r:
        hue = (60.0 * ((g - b) / delta)) % 360.0
    elif max_value == g:
        hue = 60.0 * (((b - r) / delta) + 2.0)
    else:
        hue = 60.0 * (((r - g) / delta) + 4.0)

    saturation = 0.0 if max_value == 0 else delta / max_value
    value = max_value
    return (hue, saturation, value)


def _encode_hsv_pixel(pixel: HSVPixel) -> HSVEncodedPixel:
    """Encode HSV values into Pillow's 8-bit HSV channel layout."""
    hue, saturation, value = pixel

    encoded_h = max(0, min(255, round((hue / 360.0) * 255)))
    encoded_s = max(0, min(255, round(saturation * 255)))
    encoded_v = max(0, min(255, round(value * 255)))

    return (encoded_h, encoded_s, encoded_v)
