from __future__ import annotations

from typing import Any, TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

RGBPixel: TypeAlias = tuple[int, int, int]
RGBFloatPixel: TypeAlias = tuple[float, float, float]
XYZPixel: TypeAlias = tuple[float, float, float]
LABPixel: TypeAlias = tuple[float, float, float]
LABEncodedPixel: TypeAlias = tuple[int, int, int]

__all__ = ["rgb_to_lab_conversion"]


def rgb_to_lab_conversion(img_object: PILImage) -> PILImage:
    """Convert every RGB pixel into Pillow's 8-bit LAB representation."""
    rgb_image = img_object.convert("RGB")
    _, width, height, source_pixels = _image_copy(rgb_image)
    lab_img = Image.new("LAB", (width, height))
    lab_pixels = lab_img.load()
    if lab_pixels is None:
        raise ValueError("Unable to access pixel data from the LAB image.")

    for y in range(height):
        for x in range(width):
            pixel = source_pixels[x, y]
            normalized = _normalization(pixel)
            linearized = _linearize(normalized)
            xyz_pixel = _linear_to_xyz(linearized)
            lab_pixel = _xyz_to_lab(xyz_pixel)
            lab_pixels[x, y] = _encode_lab_pixel(lab_pixel)

    return lab_img


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


def _linearize(pixel: RGBFloatPixel) -> RGBFloatPixel:
    """Apply inverse gamma correction to convert sRGB channels into linear RGB."""

    def linearize_channel(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = pixel
    return (
        linearize_channel(r),
        linearize_channel(g),
        linearize_channel(b),
    )


def _linear_to_xyz(pixel: RGBFloatPixel) -> XYZPixel:
    """Transform linear RGB values into CIE XYZ using the D65 conversion matrix."""
    r, g, b = pixel
    x_value = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y_value = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z_value = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    return (x_value, y_value, z_value)


def _xyz_to_lab(pixel: XYZPixel) -> LABPixel:
    """Convert CIE XYZ values into CIE LAB values using the D65 reference white."""

    def lab_helper(value: float) -> float:
        if value > (6 / 29) ** 3:
            return value ** (1 / 3)
        return (1 / 3) * (29 / 6) ** 2 * value + 4 / 29

    x_value, y_value, z_value = pixel
    x_ref, y_ref, z_ref = 0.95047, 1.00000, 1.08883

    l_value = 116 * lab_helper(y_value / y_ref) - 16
    a_value = 500 * (lab_helper(x_value / x_ref) - lab_helper(y_value / y_ref))
    b_value = 200 * (lab_helper(y_value / y_ref) - lab_helper(z_value / z_ref))
    return (l_value, a_value, b_value)


def _encode_lab_pixel(pixel: LABPixel) -> LABEncodedPixel:
    """Encode CIE LAB values into Pillow's 8-bit LAB channel layout."""
    l_value, a_value, b_value = pixel

    encoded_l = max(0, min(255, round((l_value / 100.0) * 255)))
    encoded_a = max(0, min(255, round(a_value + 128)))
    encoded_b = max(0, min(255, round(b_value + 128)))

    return (encoded_l, encoded_a, encoded_b)
