from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from sklearn.cluster import KMeans

def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.truetype("DejaVuSans.ttf", size)

def pixelate_image(path, size):
    img = Image.open(path).convert("RGB")
    small = img.resize((img.width // size, img.height // size), Image.NEAREST)
    return small

def upscale_image(img, size):
    return img.resize((img.width * size, img.height * size), Image.NEAREST)

def quantize_image_colors(img, n_colors=8):
    data = np.array(img)
    h, w, _ = data.shape
    flat = data.reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors, random_state=0, n_init='auto')
    labels = kmeans.fit_predict(flat)
    new_colors = kmeans.cluster_centers_.astype(np.uint8)

    quantized_flat = new_colors[labels]
    quantized_img = quantized_flat.reshape(h, w, 3)
    return Image.fromarray(quantized_img), labels.reshape(h, w), new_colors
def draw_pixel_art_grid(pixel_img, color_numbers, colors, font_size=18):
    img = pixel_img.copy()
    draw = ImageDraw.Draw(img)
    font = load_font(font_size)

    h, w = color_numbers.shape
    cell_width = img.width // w
    cell_height = img.height // h

    for y in range(h):
        for x in range(w):
            color_index = color_numbers[y, x]
            label = str(color_index + 1)  # Use numbers starting from 1
            fill_color = tuple(colors[color_index])

            top_left = (x * cell_width, y * cell_height)
            bottom_right = ((x + 1) * cell_width, (y + 1) * cell_height)

            # Draw filled block with grid outline
            draw.rectangle([top_left, bottom_right], fill=fill_color, outline="gray", width=2)

            # Decide text color based on background brightness
            contrast_color = get_contrast_color(fill_color)

            # Position text centered-ish in cell
            text_x = top_left[0] + cell_width // 3
            text_y = top_left[1] + cell_height // 3
            draw.text((text_x, text_y), label, fill=contrast_color, font=font)

    return img


def get_contrast_color(rgb):
    r, g, b = map(int, rgb)
    brightness = (r*299 + g*587 + b*114) / 1000
    return "black" if brightness > 160 else "white"

# === Main execution ===
input_path = "assets/cat.jpg"
output_path = "outputs/cat_numbered.png"
pixel_size = 30
os.makedirs("outputs", exist_ok=True)

# Step 1: Pixelate
small_img = pixelate_image(input_path, pixel_size)

# Step 2: Quantize to ~100 colors
quantized_img, color_map, colors = quantize_image_colors(small_img, n_colors=25)
image_contrast = [get_contrast_color(color) for color in colors]
# Step 3: Upscale for drawing
pixel_img = upscale_image(quantized_img, pixel_size)

# Step 4: Draw numbered grid
labeled = draw_pixel_art_grid(pixel_img, color_map, colors)



# Step 5: Save
labeled.save(output_path)
print("✅ Saved:", output_path)


