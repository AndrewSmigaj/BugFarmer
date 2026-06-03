from PIL import Image, ImageDraw
import os

output_dir = "/mnt/c/Users/emily/BugFarmer/BugFarmerClient/Assets/Resources/Objects"
os.makedirs(output_dir, exist_ok=True)

def create_plant_sprite(filename, width, height, stage, plant_color, fruit_color=None):
    """Create a plant sprite at a given growth stage"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Ground level is at the bottom
    ground_y = height - 1
    
    if stage == 0:
        # Seed stage - tiny sprout
        # Small dirt mound
        draw.ellipse([width//2-3, ground_y-2, width//2+3, ground_y], fill=(101, 67, 33, 255))
        # Tiny green sprout
        draw.line([(width//2, ground_y-2), (width//2, ground_y-5)], fill=(34, 139, 34, 255), width=1)
        draw.ellipse([width//2-2, ground_y-7, width//2+2, ground_y-5], fill=(50, 205, 50, 255))
    
    elif stage == 1:
        # Sprout stage - small plant
        stem_height = height // 3
        draw.line([(width//2, ground_y), (width//2, ground_y-stem_height)], fill=(34, 139, 34, 255), width=2)
        # Two small leaves
        draw.ellipse([width//2-4, ground_y-stem_height-3, width//2, ground_y-stem_height+3], fill=plant_color)
        draw.ellipse([width//2, ground_y-stem_height-3, width//2+4, ground_y-stem_height+3], fill=plant_color)
    
    elif stage == 2:
        # Young plant - medium size
        stem_height = height * 2 // 3
        draw.line([(width//2, ground_y), (width//2, ground_y-stem_height)], fill=(34, 139, 34, 255), width=2)
        # Multiple leaves
        for i in range(3):
            y = ground_y - stem_height//3 * (i+1)
            draw.ellipse([width//2-5, y-3, width//2-1, y+3], fill=plant_color)
            draw.ellipse([width//2+1, y-3, width//2+5, y+3], fill=plant_color)
    
    elif stage == 3:
        # Mature plant with fruit
        stem_height = height - 4
        draw.line([(width//2, ground_y), (width//2, ground_y-stem_height)], fill=(34, 139, 34, 255), width=2)
        # Full leaves
        for i in range(4):
            y = ground_y - stem_height//4 * (i+1)
            draw.ellipse([width//2-6, y-4, width//2-1, y+4], fill=plant_color)
            draw.ellipse([width//2+1, y-4, width//2+6, y+4], fill=plant_color)
        # Fruit if provided
        if fruit_color:
            draw.ellipse([width//2-3, ground_y-stem_height-2, width//2+3, ground_y-stem_height+4], fill=fruit_color)
            draw.ellipse([width//2-4, ground_y-stem_height+8, width//2+2, ground_y-stem_height+14], fill=fruit_color)
    
    img.save(os.path.join(output_dir, filename))
    print(f"Created {filename}")

# Tomato plant (16x24) - red fruit
for stage in range(4):
    fruit = (220, 20, 60, 255) if stage == 3 else None
    create_plant_sprite(f"plant_tomato_stage{stage}.png", 16, 24, stage, (34, 139, 34, 255), fruit)

# Also create base sprite (used before stage system)
create_plant_sprite("plant_tomato.png", 16, 24, 0, (34, 139, 34, 255))

# Corn plant (16x32) - yellow fruit
for stage in range(4):
    fruit = (255, 215, 0, 255) if stage == 3 else None
    create_plant_sprite(f"plant_corn_stage{stage}.png", 16, 32, stage, (50, 205, 50, 255), fruit)
create_plant_sprite("plant_corn.png", 16, 32, 0, (50, 205, 50, 255))

# Wheat plant (16x20) - golden grain
for stage in range(4):
    fruit = (218, 165, 32, 255) if stage == 3 else None  
    create_plant_sprite(f"plant_wheat_stage{stage}.png", 16, 20, stage, (154, 205, 50, 255), fruit)
create_plant_sprite("plant_wheat.png", 16, 20, 0, (154, 205, 50, 255))

print("Done! All plant sprites created.")
