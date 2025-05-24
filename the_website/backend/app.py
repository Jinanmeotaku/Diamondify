 
from PIL import Image

def pixelate_image(image_path, pixel_size, output_path):
    """
    Pixelates an image by reducing its resolution and then resizing it back to its original size.

    Args:
        image_path (str): Path to the input image file.
        pixel_size (int): Size of the pixels in the pixelated image.
        output_path (str): Path to save the pixelated image.
    """
    try:
        img = Image.open(image_path)
        width, height = img.size

        small_img = img.resize(
            (width // pixel_size, height // pixel_size), Image.NEAREST
        )
        result = small_img.resize((width, height), Image.NEAREST)
        result.save(output_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
         print(f"An error occurred: {e}")

# Example usage:
imageName = "horse.jpg"
inputPath = "assets/" + imageName
outputPath = "outputs/" + imageName
pixelate_image(inputPath, 75, outputPath)
