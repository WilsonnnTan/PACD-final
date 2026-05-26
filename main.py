from utils import decode_tiff_to_png, load_image, rgb_to_lab_conversion, save_image


def main():
    image_path = input("Input image path (default to image/image.png): ")
    if not image_path:
        image_path = "image/image.png"

    img_object = load_image(image_path)
    converted_img_object = rgb_to_lab_conversion(img_object)

    tiff_save_path = "image/image-output.tiff"
    png_save_path = "image/image_tiff_to_png.png"

    save_image(converted_img_object, tiff_save_path)
    print(f"LAB TIFF image saved on {tiff_save_path}")

    decode_tiff_to_png(tiff_save_path, png_save_path)
    print(f"TIFF image converted to PNG and saved on {png_save_path}")


if __name__ == "__main__":
    main()
