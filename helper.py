from __future__ import annotations

import copy
from os import PathLike
from typing import Any, TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

RGBAPixel: TypeAlias = tuple[int, int, int, int]
RGBAFloatPixel: TypeAlias = tuple[float, float, float, int]
XYZPixel: TypeAlias = tuple[float, float, float, int]
LABPixel: TypeAlias = tuple[float, float, float, int]
ImagePath: TypeAlias = str | PathLike[str]


class ImageLoader:
    """Handle loading and saving image files."""

    def __init__(self) -> None:
        """Initialize the image loader."""

    def load_image(self, image_path: ImagePath) -> PILImage:
        """Load an image from disk and return it as a PIL image object."""
        return Image.open(image_path)

    def save_image(self, img_object: PILImage, image_save_path: ImagePath) -> None:
        """Save a PIL image object to the given output path."""
        img_object.save(image_save_path)


class TransformingColorSpaceAlgorithm:
    """Convert image pixels from RGB color space into LAB color space."""

    def __init__(self, img_object: PILImage) -> None:
        """Store the source image that will be converted."""
        self.img_object = img_object

    def _image_deep_copy(self) -> tuple[PILImage, int, int, RGBAPixel]:
        """Clone the source image so pixel transformations do not modify the original."""
        img_object_copy = copy.deepcopy(self.img_object)
        width, height = img_object_copy.size
        pixels = img_object_copy.load()
        if pixels is None:
            raise ValueError("Unable to access pixel data from the image copy.")
        return img_object_copy, width, height, pixels

    def rgb_to_lab_conversion(self) -> PILImage:
        """Convert each pixel to LAB, then clamp the result into 8-bit image channels."""
        img_copy, width, height, pixels = self._image_deep_copy()

        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                normalized = self._normalization(pixel)
                linearized = self._linearize(normalized)
                xyz_pixel = self._linear_to_xyz(linearized)
                lab_pixel = self._xyz_to_lab(xyz_pixel)
                pixels[x, y] = self._clamp_lab_pixel(lab_pixel)

        return img_copy

    def _normalization(self, pixel: RGBAPixel) -> RGBAFloatPixel:
        """Scale 8-bit RGB channel values into the normalized range [0, 1]."""
        r, g, b, alpha = pixel
        return (r / 255.0, g / 255.0, b / 255.0, alpha)

    def _linearize(self, pixel: RGBAFloatPixel) -> RGBAFloatPixel:
        """Apply inverse gamma correction to convert sRGB channels into linear RGB."""

        def linearize_channel(channel: float) -> float:
            """Convert one sRGB channel into its linear-light equivalent."""
            if channel <= 0.04045:
                return channel / 12.92
            return ((channel + 0.055) / 1.055) ** 2.4

        r, g, b, alpha = pixel
        return (
            linearize_channel(r),
            linearize_channel(g),
            linearize_channel(b),
            alpha,
        )

    def _linear_to_xyz(self, pixel: RGBAFloatPixel) -> XYZPixel:
        """Transform linear RGB values into CIE XYZ using the D65 conversion matrix."""
        r, g, b, alpha = pixel
        x_value = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
        y_value = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        z_value = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b

        return (x_value, y_value, z_value, alpha)

    def _xyz_to_lab(self, pixel: XYZPixel) -> LABPixel:
        """Convert CIE XYZ values into CIE LAB values using the D65 reference white."""

        def lab_helper(value: float) -> float:
            """Apply the piecewise LAB helper function used in the standard formula."""
            if value > (6 / 29) ** 3:
                return value ** (1 / 3)
            return (1 / 3) * (29 / 6) ** 2 * value + 4 / 29

        x_value, y_value, z_value, alpha = pixel
        # Reference white point for the D65 illuminant in the same [0, 1] scale as XYZ.
        x_ref, y_ref, z_ref = 0.95047, 1.00000, 1.08883

        l_value = 116 * lab_helper(y_value / y_ref) - 16
        a_value = 500 * (lab_helper(x_value / x_ref) - lab_helper(y_value / y_ref))
        b_value = 200 * (lab_helper(y_value / y_ref) - lab_helper(z_value / z_ref))

        return (l_value, a_value, b_value, alpha)

    def _clamp_lab_pixel(self, pixel: LABPixel) -> RGBAPixel:
        """Clamp LAB channel values into the valid 8-bit range before saving to an image."""
        l_value, a_value, b_value, alpha = pixel
        return (
            max(0, min(255, int(l_value))),
            max(0, min(255, int(a_value))),
            max(0, min(255, int(b_value))),
            max(0, min(255, int(alpha))),
        )
