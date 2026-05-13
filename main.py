from helper import ImageLoader, TransformingColorSpaceAlgorithm


def main():
    image_path = input("Input image path (default to image/image.png): ")
    if not image_path:
        image_path = "image/image.png"
    
    image_loader = ImageLoader()
    
    img_object = image_loader.load_image(image_path)
    algorithm = TransformingColorSpaceAlgorithm(img_object)
    
    converted_img_object = algorithm.rgb_to_lab_conversion()
    
    save_path = "image/image-output.tiff"
    image_loader.save_image(converted_img_object, save_path)
    print(f"Image saved on {save_path}")


if __name__ == "__main__":
    main()
