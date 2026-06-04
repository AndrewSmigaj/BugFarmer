from PIL import Image, ImageDraw
import os

# Output directory
output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Sprites/Terrain"
os.makedirs(output_dir, exist_ok=True)

def create_garden_plot(filename, base_color, furrow_color, highlight_color):
    """Create a 16x16 tilled garden plot sprite with furrow rows"""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fill with base soil color
    draw.rectangle([0, 0, 15, 15], fill=base_color)
    
    # Draw furrow rows (tilled soil pattern)
    for y in [2, 6, 10, 14]:
        # Dark furrow line
        draw.line([(0, y), (15, y)], fill=furrow_color)
        # Highlight on top edge of mound
        if y > 0:
            draw.line([(0, y-1), (15, y-1)], fill=highlight_color)
    
    # Add some texture dots
    texture_positions = [(3, 4), (8, 8), (12, 3), (5, 12), (10, 11), (2, 9)]
    for x, y in texture_positions:
        img.putpixel((x, y), furrow_color)
    
    img.save(os.path.join(output_dir, filename))
    print(f"Created {filename}")

# Dry garden plot - brown tones
create_garden_plot(
    "garden_plot.png",
    base_color=(139, 90, 43, 255),      # Medium brown
    furrow_color=(101, 67, 33, 255),    # Dark brown
    highlight_color=(160, 110, 60, 255) # Light brown
)

# Wet garden plot - darker, richer tones
create_garden_plot(
    "garden_plot_wet.png",
    base_color=(89, 60, 31, 255),       # Dark brown (wet)
    furrow_color=(60, 40, 20, 255),     # Very dark brown
    highlight_color=(110, 75, 40, 255)  # Medium-dark brown
)

print("Done! Garden tile sprites created.")
