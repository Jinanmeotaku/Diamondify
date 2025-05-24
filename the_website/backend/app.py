from PIL import Image, ImageDraw

def pixelate_image(image_path, pixel_size, output_path, line_color=(0, 0, 0)):
    """
    Pixelates an image by reducing its resolution and then resizing it back to its original size. Then adds grid lines to an image.

    Args:
        image_path (str): Path to the input image file.
        pixel_size (int): Size of the pixels in the pixelated image, and the pixels in the grid.
        output_path (str): Path to save the pixelated image.
    """
    try:
        img = Image.open(image_path)

        width, height = img.size

        small_img = img.resize(
            (width // pixel_size, height // pixel_size), Image.NEAREST
        )
        result = small_img.resize((width, height), Image.NEAREST)
        draw = ImageDraw.Draw(result)
        for y in range(0, height, pixel_size):
            draw.line((0, y, width, y), fill=line_color)

        for x in range(0, width, pixel_size):
            draw.line((x, 0, x, height), fill=line_color)
        result.save(output_path)

    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
    except Exception as e:
         print(f"An error occurred: {e}")

# Example usage:
imageName = "cat.jpg"
inputPath = "assets/" + imageName
outputPath = "outputs/" + imageName
spacing = 50
pixelate_image(inputPath, spacing, outputPath, )
