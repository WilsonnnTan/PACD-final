from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

RGBPixel: TypeAlias = tuple[int, int, int]
RGBFloatPixel: TypeAlias = tuple[float, float, float]
XYZPixel: TypeAlias = tuple[float, float, float]
LABPixel: TypeAlias = tuple[float, float, float]
LABEncodedPixel: TypeAlias = tuple[int, int, int]

LAB_LIGHTNESS_MIN = 0.0
LAB_LIGHTNESS_MAX = 100.0
LAB_AXIS_MIN = -128.0
LAB_AXIS_MAX = 127.0
LAB_REFERENCE_WHITE: XYZPixel = (0.95047, 1.00000, 1.08883)

__all__ = [
    "LabAdjustment",
    "LabColor",
    "calculate_average_lab",
    "lab_to_rgb_conversion",
    "rgb_to_lab_conversion",
]


@dataclass(frozen=True, slots=True)
class LabAdjustment:
    """Adjust LAB values before converting them back into RGB."""

    lightness_delta: float = 0.0
    a_delta: float = 0.0
    b_delta: float = 0.0


@dataclass(frozen=True, slots=True)
class LabColor:
    """Represent one LAB color triplet using decoded channel values."""

    lightness: float
    a_value: float
    b_value: float


def rgb_to_lab_conversion(img_object: PILImage) -> PILImage:
    """Convert every RGB pixel into Pillow's 8-bit LAB representation."""
    rgb_image = img_object.convert("RGB")
    width, height = rgb_image.size
    source_pixels = rgb_image.load()
    if source_pixels is None:
        raise ValueError("Unable to access pixel data from the RGB image.")

    lab_image = Image.new("LAB", (width, height))
    lab_pixels = lab_image.load()
    if lab_pixels is None:
        raise ValueError("Unable to access pixel data from the LAB image.")

    for y in range(height):
        for x in range(width):
            normalized_pixel = _normalize_rgb_pixel(source_pixels[x, y])
            linear_rgb_pixel = _linearize_rgb_pixel(normalized_pixel)
            xyz_pixel = _linear_rgb_to_xyz(linear_rgb_pixel)
            lab_pixel = _xyz_to_lab(xyz_pixel)
            lab_pixels[x, y] = _encode_lab_pixel(lab_pixel)

    return lab_image


def lab_to_rgb_conversion(
    img_object: PILImage,
    adjustment: LabAdjustment | None = None,
) -> PILImage:
    """Convert an 8-bit LAB image back into RGB, optionally applying LAB offsets."""
    lab_image = img_object.convert("LAB")
    width, height = lab_image.size
    source_pixels = lab_image.load()
    if source_pixels is None:
        raise ValueError("Unable to access pixel data from the LAB image.")

    rgb_image = Image.new("RGB", (width, height))
    rgb_pixels = rgb_image.load()
    if rgb_pixels is None:
        raise ValueError("Unable to access pixel data from the RGB image.")

    lab_adjustment = adjustment or LabAdjustment()

    for y in range(height):
        for x in range(width):
            decoded_pixel = _decode_lab_pixel(source_pixels[x, y])
            adjusted_pixel = _apply_lab_adjustment(decoded_pixel, lab_adjustment)
            xyz_pixel = _lab_to_xyz(adjusted_pixel)
            linear_rgb_pixel = _xyz_to_linear_rgb(xyz_pixel)
            rgb_pixels[x, y] = _delinearize_rgb_pixel(linear_rgb_pixel)

    return rgb_image


def calculate_average_lab(img_object: PILImage) -> LabColor:
    """Calculate the mean decoded LAB values across the entire image."""
    lab_image = img_object.convert("LAB")
    width, height = lab_image.size
    source_pixels = lab_image.load()
    if source_pixels is None:
        raise ValueError("Unable to access pixel data from the LAB image.")

    lightness_total = 0.0
    a_total = 0.0
    b_total = 0.0
    total_pixels = width * height

    for y in range(height):
        for x in range(width):
            decoded_pixel = _decode_lab_pixel(source_pixels[x, y])
            lightness_total += decoded_pixel[0]
            a_total += decoded_pixel[1]
            b_total += decoded_pixel[2]

    return LabColor(
        lightness=lightness_total / total_pixels,
        a_value=a_total / total_pixels,
        b_value=b_total / total_pixels,
    )


def _normalize_rgb_pixel(pixel: RGBPixel) -> RGBFloatPixel:
    """Scale 8-bit RGB channel values into the normalized range [0, 1]."""
    red, green, blue = pixel
    return (red / 255.0, green / 255.0, blue / 255.0)


def _linearize_rgb_pixel(pixel: RGBFloatPixel) -> RGBFloatPixel:
    """Apply inverse gamma correction to convert sRGB values into linear RGB."""

    def linearize_channel(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = pixel
    return (
        linearize_channel(red),
        linearize_channel(green),
        linearize_channel(blue),
    )


def _linear_rgb_to_xyz(pixel: RGBFloatPixel) -> XYZPixel:
    """Transform linear RGB values into CIE XYZ using the D65 conversion matrix."""
    red, green, blue = pixel
    x_value = 0.4124564 * red + 0.3575761 * green + 0.1804375 * blue
    y_value = 0.2126729 * red + 0.7151522 * green + 0.0721750 * blue
    z_value = 0.0193339 * red + 0.1191920 * green + 0.9503041 * blue
    return (x_value, y_value, z_value)


def _xyz_to_lab(pixel: XYZPixel) -> LABPixel:
    """Convert CIE XYZ values into CIE LAB values using the D65 reference white."""

    def lab_helper(value: float) -> float:
        if value > (6 / 29) ** 3:
            return value ** (1 / 3)
        return (1 / 3) * (29 / 6) ** 2 * value + 4 / 29

    x_value, y_value, z_value = pixel
    x_ref, y_ref, z_ref = LAB_REFERENCE_WHITE

    l_value = 116 * lab_helper(y_value / y_ref) - 16
    a_value = 500 * (lab_helper(x_value / x_ref) - lab_helper(y_value / y_ref))
    b_value = 200 * (lab_helper(y_value / y_ref) - lab_helper(z_value / z_ref))
    return (l_value, a_value, b_value)


def _encode_lab_pixel(pixel: LABPixel) -> LABEncodedPixel:
    """Encode CIE LAB values into Pillow's 8-bit LAB channel layout."""
    l_value, a_value, b_value = pixel
    encoded_l = round((_clamp(l_value, LAB_LIGHTNESS_MIN, LAB_LIGHTNESS_MAX) / 100.0) * 255)
    encoded_a = round(_clamp(a_value, LAB_AXIS_MIN, LAB_AXIS_MAX) + 128.0)
    encoded_b = round(_clamp(b_value, LAB_AXIS_MIN, LAB_AXIS_MAX) + 128.0)
    return (encoded_l, encoded_a, encoded_b)


def _decode_lab_pixel(pixel: LABEncodedPixel) -> LABPixel:
    """Decode Pillow's 8-bit LAB channel layout into LAB values."""
    encoded_l, encoded_a, encoded_b = pixel
    l_value = (encoded_l / 255.0) * 100.0
    a_value = float(encoded_a - 128)
    b_value = float(encoded_b - 128)
    return (l_value, a_value, b_value)


def _apply_lab_adjustment(pixel: LABPixel, adjustment: LabAdjustment) -> LABPixel:
    """Apply channel offsets while keeping the values inside the LAB gamut."""
    l_value, a_value, b_value = pixel
    return (
        _clamp(l_value + adjustment.lightness_delta, LAB_LIGHTNESS_MIN, LAB_LIGHTNESS_MAX),
        _clamp(a_value + adjustment.a_delta, LAB_AXIS_MIN, LAB_AXIS_MAX),
        _clamp(b_value + adjustment.b_delta, LAB_AXIS_MIN, LAB_AXIS_MAX),
    )


def _lab_to_xyz(pixel: LABPixel) -> XYZPixel:
    """Convert CIE LAB values back into CIE XYZ using the D65 reference white."""

    def inverse_lab_helper(value: float) -> float:
        if value > (6 / 29):
            return value**3
        return 3 * (6 / 29) ** 2 * (value - 4 / 29)

    l_value, a_value, b_value = pixel
    fy = (l_value + 16) / 116
    fx = fy + (a_value / 500)
    fz = fy - (b_value / 200)

    x_ref, y_ref, z_ref = LAB_REFERENCE_WHITE
    x_value = x_ref * inverse_lab_helper(fx)
    y_value = y_ref * inverse_lab_helper(fy)
    z_value = z_ref * inverse_lab_helper(fz)
    return (x_value, y_value, z_value)


def _xyz_to_linear_rgb(pixel: XYZPixel) -> RGBFloatPixel:
    """Transform CIE XYZ values into linear RGB using the inverse D65 matrix."""
    x_value, y_value, z_value = pixel
    red = 3.2404542 * x_value - 1.5371385 * y_value - 0.4985314 * z_value
    green = -0.9692660 * x_value + 1.8760108 * y_value + 0.0415560 * z_value
    blue = 0.0556434 * x_value - 0.2040259 * y_value + 1.0572252 * z_value
    return (red, green, blue)


def _delinearize_rgb_pixel(pixel: RGBFloatPixel) -> RGBPixel:
    """Apply sRGB gamma correction and clamp the result back into 8-bit RGB."""

    def delinearize_channel(channel: float) -> int:
        clamped_channel = _clamp(channel, 0.0, 1.0)
        if clamped_channel <= 0.0031308:
            return round(clamped_channel * 12.92 * 255)
        return round((1.055 * (clamped_channel ** (1 / 2.4)) - 0.055) * 255)

    red, green, blue = pixel
    return (
        delinearize_channel(red),
        delinearize_channel(green),
        delinearize_channel(blue),
    )


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value into an inclusive range."""
    return max(minimum, min(maximum, value))
