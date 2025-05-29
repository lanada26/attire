# outfit_generator.py
import json
import datetime
import random
import os
from PIL import Image, ImageDraw, ImageFont

# Create directories for generated images and fonts
IMAGES_DIR = os.path.join('static', 'images')
FONTS_DIR = os.path.join('static', 'fonts')
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)
def get_previous_outfits(user_id):
    """Get a list of previously chosen outfits for a user"""
    file_path = os.path.join('data', 'training_data.json')
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            training_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
    # Return list of all chosen outfits for this user
    return [
        entry['chosen_outfit'] 
        for entry in training_data 
        if entry.get('user_id') == user_id and entry.get('chosen_outfit') is not None
    ]

def generate_outfit_recommendations(data):
    """Generate outfit recommendations using local image generation"""
    # Create outfit recommendations based on the specified occasion
    occasion = data.get('occasion', 'casual').lower()
    user_id = data.get('user_id')
    
    # Get previously chosen outfits
    previous_outfits = data.get('previous_outfits', [])
    if user_id and not previous_outfits:
        previous_outfits = get_previous_outfits(user_id)
    
    # Define outfit types with their relevance to occasions
    outfit_mapping = {
        'casual': ['casual', 'smart casual', 'athleisure', 'weekend', 'relaxed'],
        'business': ['business professional', 'business casual', 'smart casual', 'office', 'formal'],
        'evening': ['evening', 'cocktail', 'semi-formal', 'dinner', 'date night'],
        'party': ['party', 'clubbing', 'festive', 'night out', 'celebration']
    }
    
    # Ensure the occasion exists in the mapping, default to casual
    if occasion not in outfit_mapping:
        occasion = 'casual'
    
    # Get relevant outfit types for the occasion and filter out previously used ones
    outfit_types = [ot for ot in outfit_mapping.get(occasion, ['casual', 'smart casual', 'athleisure'])
                   if ot not in previous_outfits]
    
    # If we've used all outfit types, allow repeats but shuffle them
    if not outfit_types:
        outfit_types = outfit_mapping.get(occasion, ['casual', 'smart casual', 'athleisure'])
        random.shuffle(outfit_types)
    # Otherwise, limit to 3 unique outfits
    else:
        outfit_types = outfit_types[:3]
    
    outfits = []
    
    for outfit_type in outfit_types[:3]:  # Limit to 3 outfits
        # Create a new image
        image = Image.new('RGB', (300, 400), color='white')
        draw = ImageDraw.Draw(image)
        
        # Add text to the image
        text = f"{outfit_type.capitalize()} outfit for {data['gender']}"
        if 'skin_tone' in data:
            text += f" with {data['skin_tone']} skin tone"
        
        try:
            # Try to use a custom font if available
            font_path = os.path.join(FONTS_DIR, 'arial.ttf')
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 20)
            else:
                # Fallback to default font
                font = ImageFont.load_default()
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the text
        x = (image.width - text_width) // 2
        y = (image.height - text_height) // 2
        
        draw.text((x, y), text, fill="black", font=font)
        
        # Save the image
        image_path = os.path.join(IMAGES_DIR, f"outfit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{outfit_type}.png")
        image.save(image_path)
        
        # Create outfit description
        description = f"{outfit_type.capitalize()} outfit for {data['gender']}"
        if 'skin_tone' in data:
            description += f" with {data['skin_tone']} skin tone"
            
        if 'casual' in outfit_type.lower():
            description += ", perfect for a relaxed day"
        elif 'business' in outfit_type.lower():
            description += ", suitable for professional settings"
        elif 'evening' in outfit_type.lower() or 'party' in outfit_type.lower():
            description += ", great for night events"
        
        outfits.append({
            'description': description,
            'image': f"/static/images/{os.path.basename(image_path)}",
            'type': outfit_type
        })
    
    return outfits
# from PIL import Image, ImageDraw, ImageFont
# import os

# # Create directories for generated images and fonts
# IMAGES_DIR = 'static/images'
# FONTS_DIR = 'static/fonts'
# os.makedirs(IMAGES_DIR, exist_ok=True)
# os.makedirs(FONTS_DIR, exist_ok=True)

# def generate_outfit_recommendations(data):
#     """Generate outfit recommendations using local image generation"""
#     # Create 3 outfit recommendations
#     outfits = []
    
#     # Define some sample outfit types
#     outfit_types = ['casual', 'business', 'evening']
    
#     for outfit_type in outfit_types:
#         # Create a new image
#         image = Image.new('RGB', (300, 400), color='white')
#         draw = ImageDraw.Draw(image)
        
#         # Add text to the image
#         text = f"{outfit_type.capitalize()} outfit for {data['gender']} with {data['skin_tone']} skin tone"
        
#         try:
#             # Try to use a custom font if available
#             font_path = os.path.join(FONTS_DIR, 'arial.ttf')
#             if os.path.exists(font_path):
#                 font = ImageFont.truetype(font_path, 20)
#             else:
#                 # Fallback to default font
#                 font = ImageFont.load_default()
#         except:
#             # Fallback to default font
#             font = ImageFont.load_default()
        
#         # Calculate text position
#         text_bbox = draw.textbbox((0, 0), text, font=font)
#         text_width = text_bbox[2] - text_bbox[0]
#         text_height = text_bbox[3] - text_bbox[1]
        
#         # Center the text
#         x = (image.width - text_width) // 2
#         y = (image.height - text_height) // 2
        
#         draw.text((x, y), text, fill="black", font=font)
        
#         # Save the image
#         image_path = os.path.join(IMAGES_DIR, f"outfit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{outfit_type}.png")
#         image.save(image_path)
        
#         # Create outfit description
#         description = f"{outfit_type.capitalize()} outfit for {data['gender']} with {data['skin_tone']} skin tone"
#         if outfit_type == 'casual':
#             description += ", perfect for a relaxed day"
#         elif outfit_type == 'business':
#             description += ", suitable for professional settings"
#         else:
#             description += ", ideal for evening events"
        
#         outfits.append({
#             'description': description,
#             'image': f"/static/images/{os.path.basename(image_path)}",
#             'type': outfit_type
#         })
    
#     return outfits