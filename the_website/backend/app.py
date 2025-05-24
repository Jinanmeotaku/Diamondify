from flask import Flask, request, jsonify, send_from_directory,send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
import os
import time
import logging
import numpy as np
from sklearn.cluster import KMeans

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Use absolute paths for upload and output folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'assets')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')

logger.debug(f"Creating directories: {UPLOAD_FOLDER} and {OUTPUT_FOLDER}")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ----- IMAGE PROCESSING FUNCTIONS -----

def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.truetype("DejaVuSans.ttf", size)

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

def get_contrast_color(rgb):
    r, g, b = map(int, rgb)
    brightness = (r*299 + g*587 + b*114) / 1000
    return "black" if brightness > 160 else "white"

def draw_pixel_art_grid(pixel_img, color_numbers, colors, font_size=16):
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

def pixelate_and_label_image(input_path, output_path, pixel_size=30, n_colors=25):
    img = Image.open(input_path).convert("RGB")
    small = img.resize((img.width // pixel_size, img.height // pixel_size), Image.NEAREST)
    quantized_img, color_map, colors = quantize_image_colors(small, n_colors=n_colors)
    pixel_img = quantized_img.resize((quantized_img.width * pixel_size, quantized_img.height * pixel_size), Image.NEAREST)
    labeled = draw_pixel_art_grid(pixel_img, color_map, colors, font_size=max(8, pixel_size // 2))
    labeled.save(output_path)
    return True

def reduce_colors(image_path, num_colors=32, output_path=None):
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        reduced_img = img.quantize(colors=num_colors).convert('RGB')
        if output_path:
            reduced_img.save(output_path)
        return reduced_img
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def analyze_colors(image_path, num_colors=32):
    try:
        reduced_img = reduce_colors(image_path, num_colors)
        if reduced_img is None:
            return {}

        pixels = reduced_img.getdata()
        color_counts = Counter(pixels)

        color_analysis = {}
        for rgb, count in color_counts.items():
            hex_code = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
            color_analysis[hex_code] = {
                'count': count,
                'rgb': rgb
            }

        color_analysis = dict(sorted(color_analysis.items(),
                                     key=lambda x: x[1]['count'],
                                     reverse=True))
        return color_analysis
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# ----- FLASK ROUTES -----

@app.route('/generate', methods=['POST'])
def generate():
    try:
        if 'image' not in request.files:
            logger.error("No image file in request")
            return jsonify({'error': 'No image file provided'}), 400
            
        file = request.files['image']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No selected file'}), 400

        # Get pixel size with default
        pixel_size = int(request.form.get('pixel_size', 50))
        logger.debug(f"Processing with pixel_size={pixel_size}")

        filename = secure_filename(file.filename)
        # Add timestamp to filename to prevent overwriting
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{int(time.time())}{ext}"
        
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        
        logger.debug(f"Saving uploaded file to: {input_path}")
        file.save(input_path)
        
        logger.debug("Starting image processing")
        if not pixelate_and_label_image(input_path, output_path, pixel_size):
            return jsonify({'error': 'Failed to process image'}), 500
            
        logger.debug("Analyzing colors")
        colors = analyze_colors(output_path, num_colors=32)
        
        logger.debug("Generation complete")
        return jsonify({
            'success': True,
            'image_url': f'/outputs/{filename}',
            'colors': colors
        })
        
    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory(app.static_folder, 'style.css')

@app.route('/outputs/<filename>')
def serve_output(filename):
    try:
        logger.debug(f"Serving output file: {filename}")
        return send_from_directory(OUTPUT_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving output file: {str(e)}")
        return jsonify({'error': str(e)}), 404
    
@app.route("/download/<filename>")
def download(filename):
    try:
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
