from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from PIL import Image, ImageDraw, ImageOps, ImageTk
from PIL.Image import Image as PILImage

from utils import (
    decode_tiff_to_png,
    load_image,
    rgb_to_grayscale_average_conversion,
    rgb_to_hsv_conversion,
    rgb_to_lab_conversion,
    save_image,
)

PREVIEW_IMAGE_SIZE = (320, 320)
DEFAULT_IMAGE_PATH = Path("image/image.png")
GENERATED_SOURCE_IMAGE_PATH = Path("image/generated-image.png")


def main():
    resolved_image_path = resolve_image_path()

    img_object = load_image(resolved_image_path)
    grayscale_img = rgb_to_grayscale_average_conversion(img_object)
    hsv_img = rgb_to_hsv_conversion(img_object)
    lab_img = rgb_to_lab_conversion(img_object)

    grayscale_save_path = "image/image-grayscale-output.png"
    lab_tiff_save_path = "image/image-lab-output.tiff"
    lab_png_preview_path = "image/image-lab-preview.png"

    save_image(grayscale_img, grayscale_save_path)
    print(f"Grayscale image saved on {grayscale_save_path}")

    save_image(lab_img, lab_tiff_save_path)
    print(f"LAB TIFF image saved on {lab_tiff_save_path}")

    decode_tiff_to_png(lab_tiff_save_path, lab_png_preview_path)
    print(f"TIFF image converted to PNG and saved on {lab_png_preview_path}")

    preview_sections = [
        [
            ("Original RGB", img_object, "image/image-original-preview.png"),
            ("Grayscale Average", grayscale_img, "image/image-grayscale-output.png"),
        ],
        [
            ("HSV Hue (H)", _create_hue_preview(hsv_img), "image/image-h-channel.png"),
            ("HSV Saturation (S)", _create_saturation_preview(hsv_img), "image/image-s-channel.png"),
            ("HSV Value (V)", _extract_grayscale_channel_preview(hsv_img, 2), "image/image-v-channel.png"),
        ],
        [
            ("LAB Lightness (L)", _extract_grayscale_channel_preview(lab_img, 0), "image/image-l-channel.png"),
            ("LAB A Channel (A)", _create_lab_a_preview(lab_img), "image/image-a-channel.png"),
            ("LAB B Channel (B)", _create_lab_b_preview(lab_img), "image/image-b-channel.png"),
        ],
    ]
    save_preview_images(preview_sections)
    show_transformation_gallery(preview_sections)


def resolve_image_path() -> str:
    """Resolve the default image path or generate a source image when it is missing."""
    if DEFAULT_IMAGE_PATH.exists():
        return str(DEFAULT_IMAGE_PATH)

    generated_image_path = generate_default_image()
    print(f"Default image not found. Generated a new source image: {generated_image_path}")
    return str(generated_image_path)


def generate_default_image() -> Path:
    """Generate a colorful source image so the transformations can still run."""
    GENERATED_SOURCE_IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    width, height = 640, 640
    generated_image = Image.new("RGB", (width, height))
    pixels = generated_image.load()
    if pixels is None:
        raise ValueError("Unable to access pixel data for generated source image.")

    for y in range(height):
        for x in range(width):
            red = round((x / (width - 1)) * 255)
            green = round((y / (height - 1)) * 255)
            blue = round((((x + y) / 2) / ((width + height) / 2 - 1)) * 255)
            pixels[x, y] = (red, green, blue)

    draw = ImageDraw.Draw(generated_image)
    draw.ellipse((60, 60, 280, 280), outline=(255, 255, 255), width=10, fill=(255, 80, 80))
    draw.rectangle((360, 80, 580, 260), outline=(20, 20, 20), width=8, fill=(70, 180, 255))
    draw.polygon([(120, 500), (320, 320), (520, 500)], outline=(255, 255, 255), fill=(255, 220, 60))
    draw.line((40, 600, 600, 40), fill=(0, 0, 0), width=6)

    save_image(generated_image, GENERATED_SOURCE_IMAGE_PATH)
    return GENERATED_SOURCE_IMAGE_PATH


def save_preview_images(preview_sections: list[list[tuple[str, PILImage, str]]]) -> None:
    """Save every preview image shown in the Tkinter gallery."""
    for preview_images in preview_sections:
        for title, img_object, save_path in preview_images:
            save_image(img_object, save_path)
            print(f"{title} preview saved on {save_path}")


def show_transformation_gallery(preview_sections: list[list[tuple[str, PILImage, str]]]) -> None:
    """Render a Tkinter window that displays the source image and conversions."""
    root = tk.Tk()
    root.title("Image Transformation Preview")

    container = ttk.Frame(root, padding=16)
    container.grid(sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    photo_images: list[ImageTk.PhotoImage] = []

    max_columns = max(len(preview_images) for preview_images in preview_sections)

    for row, preview_images in enumerate(preview_sections):
        for column, (title, img_object, _) in enumerate(preview_images):
            frame = ttk.Frame(container, padding=12)
            frame.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")

            preview_image = _prepare_preview_image(img_object)
            photo_image = ImageTk.PhotoImage(preview_image)
            photo_images.append(photo_image)

            title_label = ttk.Label(frame, text=title)
            title_label.pack(pady=(0, 8))

            image_label = ttk.Label(frame, image=photo_image)
            image_label.pack()

    for column in range(max_columns):
        container.columnconfigure(column, weight=1)
    for row in range(len(preview_sections)):
        container.rowconfigure(row, weight=1)

    root.photo_images = photo_images
    root.mainloop()


def _prepare_preview_image(img_object: PILImage) -> PILImage:
    """Convert transformed images into Tkinter-friendly RGB previews."""
    preview_image = img_object.convert("RGB")

    return ImageOps.contain(preview_image, PREVIEW_IMAGE_SIZE)


def _extract_grayscale_channel_preview(img_object: PILImage, channel_index: int) -> PILImage:
    """Extract one channel and normalize it for clearer grayscale previewing."""
    channels = img_object.split()
    if channel_index >= len(channels):
        raise ValueError(f"Channel index {channel_index} is out of range for mode {img_object.mode}.")
    channel_image = channels[channel_index].copy()
    channel_min, channel_max = channel_image.getextrema()
    if channel_min == channel_max:
        return channel_image
    return ImageOps.autocontrast(channel_image)


def _create_hue_preview(hsv_img: PILImage) -> PILImage:
    """Visualize hue as a full-color spectrum while ignoring source saturation and value."""
    hue_channel = hsv_img.split()[0]
    full_saturation = Image.new("L", hsv_img.size, 255)
    full_value = Image.new("L", hsv_img.size, 255)
    return Image.merge("HSV", (hue_channel, full_saturation, full_value)).convert("RGB")


def _create_saturation_preview(hsv_img: PILImage) -> PILImage:
    """Visualize saturation using a fixed red hue and full brightness."""
    saturation_channel = _extract_grayscale_channel_preview(hsv_img, 1)
    fixed_hue = Image.new("L", hsv_img.size, 0)
    full_value = Image.new("L", hsv_img.size, 255)
    return Image.merge("HSV", (fixed_hue, saturation_channel, full_value)).convert("RGB")


def _create_lab_a_preview(lab_img: PILImage) -> PILImage:
    """Visualize the LAB A axis from green through neutral gray to magenta."""
    return _create_centered_axis_preview(
        lab_img.split()[1],
        negative_color=(0, 255, 0),
        positive_color=(255, 0, 255),
    )


def _create_lab_b_preview(lab_img: PILImage) -> PILImage:
    """Visualize the LAB B axis from blue through neutral gray to yellow."""
    return _create_centered_axis_preview(
        lab_img.split()[2],
        negative_color=(0, 0, 255),
        positive_color=(255, 255, 0),
    )


def _create_centered_axis_preview(
    channel_image: PILImage,
    negative_color: tuple[int, int, int],
    positive_color: tuple[int, int, int],
) -> PILImage:
    """Map a centered channel around 128 into an intuitive false-color preview."""
    preview_image = Image.new("RGB", channel_image.size)
    source_pixels = channel_image.load()
    preview_pixels = preview_image.load()
    if source_pixels is None or preview_pixels is None:
        raise ValueError("Unable to access pixel data for channel preview generation.")

    width, height = channel_image.size
    neutral = (128, 128, 128)

    for y in range(height):
        for x in range(width):
            encoded_value = source_pixels[x, y]
            offset = encoded_value - 128
            strength = min(1.0, abs(offset) / 127.0)
            target_color = positive_color if offset >= 0 else negative_color
            preview_pixels[x, y] = _blend_rgb(neutral, target_color, strength)

    return preview_image


def _blend_rgb(
    start_color: tuple[int, int, int],
    end_color: tuple[int, int, int],
    strength: float,
) -> tuple[int, int, int]:
    """Blend two RGB colors using a strength value in the range [0, 1]."""
    return tuple(
        round(start_channel + (end_channel - start_channel) * strength)
        for start_channel, end_channel in zip(start_color, end_color, strict=True)
    )


if __name__ == "__main__":
    main()
