from __future__ import annotations

from os import PathLike
from typing import Any, TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

RGBPixel: TypeAlias = tuple[int, int, int]
RGBFloatPixel: TypeAlias = tuple[float, float, float]
XYZPixel: TypeAlias = tuple[float, float, float]
LABPixel: TypeAlias = tuple[float, float, float]
LABEncodedPixel: TypeAlias = tuple[int, int, int]
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

    def decode_tiff_to_png(
        self,
        tiff_path: ImagePath,
        png_save_path: ImagePath = "image_tiff_to_png.png",
    ) -> PILImage:
        """Decode a TIFF image into RGB and save it as a PNG preview image."""
        img_object = self.load_image(tiff_path)
        png_ready_image = img_object.convert("RGB")
        self.save_image(png_ready_image, png_save_path)
        return png_ready_image


class TransformingColorSpaceAlgorithm:
    """Convert an RGB image into a PIL LAB image."""

    def __init__(self, img_object: PILImage) -> None:
        """Store the source image and normalize it to RGB for LAB conversion."""
        self.img_object = img_object.convert("RGB")

    def _image_copy(self) -> tuple[PILImage, int, int, Any]:
        """Create a copy of the RGB source image and expose its pixel access object."""
        img_object_copy = self.img_object.copy()
        width, height = img_object_copy.size
        pixels = img_object_copy.load()
        if pixels is None:
            raise ValueError("Unable to access pixel data from the source image copy.")
        return img_object_copy, width, height, pixels

    def rgb_to_lab_conversion(self) -> PILImage:
        """Convert every RGB pixel into PIL's 8-bit LAB representation."""
        _, width, height, source_pixels = self._image_copy()
        lab_img = Image.new("LAB", (width, height))
        lab_pixels = lab_img.load()
        if lab_pixels is None:
            raise ValueError("Unable to access pixel data from the LAB image.")

        for y in range(height):
            for x in range(width):
                pixel = source_pixels[x, y]
                normalized = self._normalization(pixel)
                linearized = self._linearize(normalized)
                xyz_pixel = self._linear_to_xyz(linearized)
                lab_pixel = self._xyz_to_lab(xyz_pixel)
                lab_pixels[x, y] = self._encode_lab_pixel(lab_pixel)

        return lab_img

    def _normalization(self, pixel: RGBPixel) -> RGBFloatPixel:
        """Scale 8-bit RGB channel values into the normalized range [0, 1]."""
        r, g, b = pixel
        return (r / 255.0, g / 255.0, b / 255.0)

    def _linearize(self, pixel: RGBFloatPixel) -> RGBFloatPixel:
        """Apply inverse gamma correction to convert sRGB channels into linear RGB."""

        def linearize_channel(channel: float) -> float:
            """Convert one sRGB channel into its linear-light equivalent."""
            if channel <= 0.04045:
                return channel / 12.92
            return ((channel + 0.055) / 1.055) ** 2.4

        r, g, b = pixel
        return (
            linearize_channel(r),
            linearize_channel(g),
            linearize_channel(b),
        )

    def _linear_to_xyz(self, pixel: RGBFloatPixel) -> XYZPixel:
        """Transform linear RGB values into CIE XYZ using the D65 conversion matrix."""
        r, g, b = pixel
        x_value = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
        y_value = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        z_value = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
        return (x_value, y_value, z_value)

    def _xyz_to_lab(self, pixel: XYZPixel) -> LABPixel:
        """Convert CIE XYZ values into CIE LAB values using the D65 reference white."""

        def lab_helper(value: float) -> float:
            """Apply the piecewise LAB helper function used in the standard formula."""
            if value > (6 / 29) ** 3:
                return value ** (1 / 3)
            return (1 / 3) * (29 / 6) ** 2 * value + 4 / 29

        x_value, y_value, z_value = pixel
        # Reference white point for the D65 illuminant in the same [0, 1] scale as XYZ.
        x_ref, y_ref, z_ref = 0.95047, 1.00000, 1.08883

        l_value = 116 * lab_helper(y_value / y_ref) - 16
        a_value = 500 * (lab_helper(x_value / x_ref) - lab_helper(y_value / y_ref))
        b_value = 200 * (lab_helper(y_value / y_ref) - lab_helper(z_value / z_ref))
        return (l_value, a_value, b_value)

    def _encode_lab_pixel(self, pixel: LABPixel) -> LABEncodedPixel:
        """Encode CIE LAB values into Pillow's 8-bit LAB channel layout."""
        l_value, a_value, b_value = pixel

        encoded_l = max(0, min(255, round((l_value / 100.0) * 255)))
        encoded_a = max(0, min(255, round(a_value + 128)))
        encoded_b = max(0, min(255, round(b_value + 128)))

        return (encoded_l, encoded_a, encoded_b)
