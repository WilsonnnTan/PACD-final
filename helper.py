from PIL import Image
import copy

class ImageLoader:
    def __init__(self):
        pass
      
    def load_image(self, image_path):
        """
        Load an image from the specified file path.
        
        Args:
            image_path (str): The file path to the image file.
        
        Returns:
            img_object (PIL.Image): The PIL Image object.
        """
        
        img_object = Image.open(image_path)
        
        return img_object

    def save_image(self, img_object, image_save_path) -> None:
        """
        Save an image to the specified file path.
        
        Args:
            img_object (PIL.Image): The PIL Image object to save.
            image_save_path (str): The file path where the image will be saved.
        
        Returns:
            None
        """
        
        img_object.save(image_save_path)
        

class TransformingColorSpaceAlgorithm:
    def __init__(self, img_object):
        """
        Initialize the TransformingColorSpaceAlgorithm with an image object.
        
        Args:
            img_object (PIL.Image): The PIL Image object to convert.
        """
        self.img_object = img_object
        
    def _image_deep_copy(self):
        """
        Create a deep copy of the image object and extract its properties.
        
        This is a private helper method that creates an independent copy of the
        original image to avoid modifying the source image when applying filters.
        
        Returns:
            tuple: A tuple containing:
                - img_object_copy (PIL.Image): A deep copy of the image.
                - width (int): The width of the image in pixels.
                - height (int): The height of the image in pixels.
                - pixels: PIL Image pixel data object for the copied image.
        """
        img_object_copy = copy.deepcopy(self.img_object)
        width, height = img_object_copy.size
        pixels = img_object_copy.load()
        
        return (img_object_copy, width, height, pixels)
    