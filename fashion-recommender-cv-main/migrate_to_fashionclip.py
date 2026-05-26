import os
import pickle
import chromadb
import torch
import argparse
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm

def migrate(limit=None):
    print("Loading image paths...")
    with open("img_paths.pkl", "rb") as f:
        image_paths = pickle.load(f)
    
    if limit:
        image_paths = image_paths[:limit]
        print(f"Limiting to {limit} images for demonstration.")

    print("Initializing FashionCLIP...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # We use patrickjohncyh/fashion-clip which is a standard choice for FashionCLIP
    model_name = "patrickjohncyh/fashion-clip"
    processor = CLIPProcessor.from_pretrained(model_name)
    model = CLIPModel.from_pretrained(model_name).to(device)
    model.eval()

    print("Initializing ChromaDB...")
    # Initialize ChromaDB persistent client
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Create or get collection
    collection = chroma_client.get_or_create_collection(
        name="fashion_items",
        metadata={"hnsw:space": "cosine"} # cosine similarity is standard for CLIP
    )

    batch_size = 32
    print(f"Processing {len(image_paths)} images in batches of {batch_size}...")

    # Process in batches
    for i in tqdm(range(0, len(image_paths), batch_size)):
        batch_paths = image_paths[i:i + batch_size]
        
        # Load images
        valid_images = []
        valid_paths = []
        for path in batch_paths:
            try:
                # Some paths in pickle might be relative, ensure they exist
                if os.path.exists(path):
                    img = Image.open(path).convert("RGB")
                    valid_images.append(img)
                    valid_paths.append(path)
            except Exception as e:
                print(f"Error loading {path}: {e}")
                continue

        if not valid_images:
            continue

        # Generate embeddings
        with torch.no_grad():
            inputs = processor(images=valid_images, return_tensors="pt", padding=True).to(device)
            image_features = model.get_image_features(**inputs)
            if not isinstance(image_features, torch.Tensor):
                image_features = image_features.pooler_output
            # Normalize embeddings
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            embeddings = image_features.cpu().numpy().tolist()

        # Generate IDs and Metadata
        ids = [f"item_{i+j}" for j in range(len(valid_paths))]
        
        # Extract basic metadata from filename (e.g., category) if possible
        # format: ./index_images/hash_Category_ID.jpg
        metadatas = []
        for path in valid_paths:
            basename = os.path.basename(path)
            parts = basename.split("_")
            category = "Unknown"
            if len(parts) > 2:
                category = "_".join(parts[1:-1]) # Extract category from filename
            metadatas.append({"path": path, "category": category})

        # Add to ChromaDB
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    print(f"Migration complete. {collection.count()} items currently in ChromaDB collection.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of images to process")
    args = parser.parse_args()
    migrate(limit=args.limit)
