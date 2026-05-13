from helper import ImageLoader, TransformingColorSpaceAlgorithm


def main():
    image_path = input("Input image path (default to image/image.png): ")
    if not image_path:
        image_path = "image/image.png"
    
    image_loader = ImageLoader()
    
    img_object = image_loader.load_image(image_path)
    algorithm = TransformingColorSpaceAlgorithm(img_object)
    
    converted_img_object = algorithm.rgb_to_lab_conversion()
    
    tiff_save_path = "image/image-output.tiff"
    png_save_path = "image/image_tiff_to_png.png"

    image_loader.save_image(converted_img_object, tiff_save_path)
    print(f"LAB TIFF image saved on {tiff_save_path}")

    image_loader.decode_tiff_to_png(tiff_save_path, png_save_path)
    print(f"TIFF image converted to PNG and saved on {png_save_path}")


if __name__ == "__main__":
    main()
