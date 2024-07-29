from PIL import Image

def print_pixel_values_in_grid(image_path):
    # Open an image file
    with Image.open(image_path) as img:
        # Convert image to RGB if not already in that mode
        img = img.convert('RGB')
        
        # Load image data
        pixels = img.load()
        width, height = img.size
        
        # Iterate through each row
        for y in range(height):
            row_values = []
            for x in range(width):
                row_values.append(f"{pixels[x, y]}")
            print(" ".join(row_values))

# Provide the path to your image
image_path = '/liujinxin/code/models/PSALM/datasets/coco_all/bottle/panoptic_train2017/bottle/defective/5.png'
print_pixel_values_in_grid(image_path)
