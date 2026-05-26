from __future__ import annotations

from os import PathLike
from typing import TypeAlias

from PIL import Image
from PIL.Image import Image as PILImage

ImagePath: TypeAlias = str | PathLike[str]

__all__ = ["load_image", "save_image", "decode_tiff_to_png"]


def load_image(image_path: ImagePath) -> PILImage:
    """Load an image from disk and return it as a PIL image object."""
    with Image.open(image_path) as img_object:
        return img_object.copy()


def save_image(img_object: PILImage, image_save_path: ImagePath) -> None:
    """Save a PIL image object to the given output path."""
    img_object.save(image_save_path)


def decode_tiff_to_png(
    tiff_path: ImagePath,
    png_save_path: ImagePath = "image_tiff_to_png.png",
) -> PILImage:
    """Decode a TIFF image into RGB and save it as a PNG preview image."""
    img_object = load_image(tiff_path)
    png_ready_image = img_object.convert("RGB")
    save_image(png_ready_image, png_save_path)
    return png_ready_image
