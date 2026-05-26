import os
import json
import random
import urllib.parse

import numpy as np
from PIL import Image

OCCASION_OPTIONS = [
    "Any",
    "Casual",
    "Work",
    "Date Night",
    "Party",
    "Beach",
    "Travel",
    "Outdoor",
    "Wedding",
    "Gala"
]

OCCASION_MAP = {
    'Dresses': ['Date Night', 'Party', 'Wedding', 'Gala'],
    'Skirts': ['Casual', 'Date Night', 'Work'],
    'Coats': ['Outdoor', 'Work', 'Casual'],
    'Shirts': ['Work', 'Casual', 'Travel'],
    'Pants': ['Work', 'Casual', 'Travel'],
    'Shorts': ['Beach', 'Travel', 'Casual'],
    'Swimwear': ['Beach', 'Travel'],
    'Jumpsuits': ['Party', 'Date Night', 'Travel'],
    'Shoes': ['Work', 'Casual', 'Gala'],
    'Handbags': ['Party', 'Work', 'Date Night'],
    'Scarves': ['Work', 'Outdoor', 'Casual'],
    'Hats': ['Outdoor', 'Beach', 'Casual'],
    'Jewelry': ['Party', 'Gala', 'Date Night'],
    'Belts': ['Work', 'Casual'],
    'Sunglasses': ['Beach', 'Outdoor', 'Travel'],
    'Gloves': ['Outdoor', 'Work'],
    'Watches': ['Work', 'Casual', 'Travel'],
    'Socks': ['Work', 'Casual', 'Travel'],
    'Neckties': ['Work', 'Gala'],
    'Rings': ['Party', 'Gala'],
    'Stockings': ['Party', 'Date Night']
}

USER_FILE = 'users.json'


def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def get_dominant_colors(pil_image, n_colors=4):
    image = pil_image.convert('RGB').resize((120, 120))
    pixels = np.array(image).reshape(-1, 3)
    pixels = pixels[(pixels.sum(axis=1) > 30)]
    if pixels.shape[0] == 0:
        return [(255, 255, 255)]

    quantized = (pixels // 32) * 32
    uniques, counts = np.unique(quantized, axis=0, return_counts=True)
    order = np.argsort(-counts)
    colors = [tuple(uniques[i]) for i in order[:n_colors]]
    while len(colors) < n_colors:
        colors.append((255, 255, 255))
    return colors


def color_harmony_score(colors):
    if len(colors) < 2:
        return 0.0
    values = np.array(colors, dtype=float)
    pairs = []
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            pairs.append(np.linalg.norm(values[i] - values[j]))
    return float(np.mean(pairs)) if pairs else 0.0


def ai_outfit_rating(detected_labels, dominant_colors, occasion):
    score = 2
    score += min(2, max(0, len(detected_labels) - 1))
    harmony = color_harmony_score(dominant_colors[:3])
    if harmony > 45:
        score += 1
    if harmony > 80:
        score += 1
    score = min(5, max(1, int(round(score))))

    label_text = ' and '.join(detected_labels[:3]) if detected_labels else 'an outfit'
    occasion_text = f' for {occasion}' if occasion and occasion != 'Any' else ''
    if score >= 4:
        commentary = f'{label_text.capitalize()} creates a strong fashion statement{occasion_text}. The color palette is balanced and modern.'
    elif score == 3:
        commentary = f'{label_text.capitalize()} has good structure{occasion_text}, with room to elevate the color harmony.'
    else:
        commentary = f'{label_text.capitalize()} feels experimental{occasion_text}. Try introducing contrast or a refined accent color.'

    return score, commentary


def map_class_to_occasions(item_class):
    return OCCASION_MAP.get(item_class, ['Casual', 'Work', 'Date Night'])


def build_shopping_link(item_label, dominant_colors=None):
    query_label = item_label.replace(' ', '+')
    color_part = ''
    if dominant_colors:
        color_part = '+' + '+'.join([rgb_to_hex(c).replace('#', '') for c in dominant_colors[:1]])
    query = f'https://www.google.com/search?q={query_label}+fashion+item{color_part}'
    return query


def get_shopping_recommendations(detected_labels, dominant_colors=None):
    recommendations = []
    for label in detected_labels[:3]:
        url = build_shopping_link(label, dominant_colors)
        recommendations.append({'label': label, 'link': url})
    return recommendations


def save_user_profile(username, password, wardrobe=None):
    if wardrobe is None:
        wardrobe = []
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}

    users[username] = {'password': password, 'wardrobe': wardrobe}
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def load_user_profile(username):
    if not os.path.exists(USER_FILE):
        return None
    with open(USER_FILE, 'r', encoding='utf-8') as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            return None
    return users.get(username)


def authenticate_user(username, password):
    profile = load_user_profile(username)
    if not profile:
        return False
    return profile.get('password') == password


def save_wardrobe_item(username, image, labels, occasion, dominant_colors):
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}

    profile = users.get(username, {'password': '', 'wardrobe': []})
    wardrobe_folder = os.path.join('wardrobe', username)
    os.makedirs(wardrobe_folder, exist_ok=True)
    file_name = f"outfit_{len(profile['wardrobe']) + 1}.png"
    image_path = os.path.join(wardrobe_folder, file_name)
    image.save(image_path)

    profile['wardrobe'].append({
        'image_path': image_path,
        'labels': labels,
        'occasion': occasion,
        'colors': [rgb_to_hex(c) for c in dominant_colors[:4]]
    })

    users[username] = profile
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def get_user_wardrobe(username):
    profile = load_user_profile(username)
    if not profile:
        return []
    return profile.get('wardrobe', [])
