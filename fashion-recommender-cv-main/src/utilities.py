import torch
import gc
import faiss
import random

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from torchvision import transforms
from tqdm import tqdm
from PIL import Image

import chromadb
from transformers import CLIPProcessor, CLIPModel

class FashionCLIPEmbedder:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = "patrickjohncyh/fashion-clip"
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
    def embed_image(self, image_array):
        pil_image = Image.fromarray(image_array).convert("RGB")
        with torch.no_grad():
            inputs = self.processor(images=pil_image, return_tensors="pt", padding=True).to(self.device)
            image_features = self.model.get_image_features(**inputs)
            if not isinstance(image_features, torch.Tensor):
                image_features = image_features.pooler_output
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            return image_features.cpu().numpy().tolist()[0]
            
    def embed_text(self, text):
        with torch.no_grad():
            inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
            text_features = self.model.get_text_features(**inputs)
            if not isinstance(text_features, torch.Tensor):
                text_features = text_features.pooler_output
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            return text_features.cpu().numpy().tolist()[0]

def get_chroma_collection():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_or_create_collection("fashion_items", metadata={"hnsw:space": "cosine"})

def display_image(file_name):
    try:
        img = Image.open(file_name)
        plt.imshow(img)
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"An error occured: {e}")


def visualize_nearest_neighbors(selected_img_path, nearest_neighbor_paths):
    # Create a figure with two columns
    fig, axs = plt.subplots(5, 2, figsize=(10, 8))

    plt.suptitle("Recommended Items based on your selection", fontsize=16, y=1.03)

    # Display the item selected in the first column (column 0)
    selected_img = mpimg.imread(selected_img_path)
    axs[0, 0].imshow(selected_img)
    axs[0, 0].set_title("Item selected")
    axs[0, 0].axis('off')

    # Limit the number of displayed neighbors to a maximum of 10
    num_neighbors = min(len(nearest_neighbor_paths), 10)

    # Loop through the recommended items (nearest neighbors) and display them in the second column (column 1)
    for i, ax in enumerate(axs[1:].flatten(), 1):
        if i <= num_neighbors:
            neighbor_path = nearest_neighbor_paths[i - 1]
            img = mpimg.imread(neighbor_path)
            ax.imshow(img)
            ax.set_title(f"Recommended Item {i}")
            ax.axis('off')

    # Hide the axis line in the second column of the first row
    for i in range(5):
        axs[i, 0].axis('off')
        axs[i, 1].axis('off')

    # Show the images
    return fig

def extract_img_clip(image, embedder):
    return embedder.embed_image(image)

def similar_img_search_chroma(query_vector, collection, n_results=6, where=None, include_distances=False):
    query_kwargs = {
        "query_embeddings": [query_vector],
        "n_results": n_results
    }
    if where:
        query_kwargs["where"] = where
        
    results = collection.query(**query_kwargs)
    
    if not results['metadatas'] or not results['metadatas'][0]:
        return [] if not include_distances else ([], [])

    paths = [meta["path"] for meta in results['metadatas'][0]]
    if include_distances and results.get("distances"):
        return paths, results["distances"][0]
    return paths

def visualize_outfits(boards):
    # Create a figure with two columns
    fig, axs = plt.subplots(4, 2, figsize=(10, 8))

    plt.suptitle("Recommended items based on detected fashion objects", fontsize=14, y=1)

    # Limit the number of displayed neighbors to a maximum of 6
    num_neighbors = min(len(boards), 6)
    
    # randomly select 6 paths to display
    random_paths = random.sample(boards, num_neighbors)

    # Loop through the recommended items and display them
    for i, ax in enumerate(axs.flatten()):
        if i < len(random_paths):
            neigbor_path = random_paths[i]
            img = mpimg.imread(neigbor_path)
            ax.imshow(img)
            ax.axis('off')

    # Hide the axis line in the all axes
    for i in range(4):
        axs[i, 0].axis('off')
        axs[i, 1].axis('off')

    return fig

def viz_thumbnail(im_path, tn_sz):
    a_img = mpimg.imread(im_path)
    # Get the dimensions of the original image
    img_height, img_width, _ = a_img.shape

    # Calculate the padding needed to make the image square
    max_dim = max(img_height, img_width)
    pad_vert = (max_dim - img_height) // 2
    pad_horiz = (max_dim - img_width) // 2

    # Create new image with padding
    padded_img = np.pad(a_img, ((pad_vert, pad_vert), (pad_horiz, pad_horiz), (0, 0)), mode='constant', constant_values=255)

    # Create fig and axis
    fig, ax = plt.subplots(figsize=tn_sz)

    ax.imshow(padded_img)

    # remove axes ticks and labels for a cleaner look
    ax.axis('off')

    return fig
