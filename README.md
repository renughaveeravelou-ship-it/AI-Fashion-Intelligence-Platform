# Smart Stylist – AI-Powered Fashion Intelligence Platform
    
## Overview
Smart Stylist is an advanced AI-powered fashion intelligence platform that combines Computer Vision, Deep Learning, Recommendation Systems, and Multi-Modal AI to deliver smart fashion recommendations and styling assistance.

## The platform allows users to: 
- Upload outfit images
- Detect fashion objects using YOLO
- Search visually similar outfits
- Perform multi-modal fashion search
- Get AI-generated outfit ratings
- Use voice-powered fashion search
- Generate AI captions
- Try virtual outfit previews
- Receive personalized recommendations
- Explore fashion trends with AI analytics

## This project supports:
 - Streamlit-based AI application
 - Full Stack React + FastAPI architecture
 - AI Fashion Search Engine 
 - FashionCLIP embeddings
 - Personalized recommendation engine
 - ChromaDB vector database integration

## Key Features 
### AI-Powered Fashion Features

- Advanced AI Ensemble Search Combines:
      - YOLO Object Detection
      - Fashion CLIP Embeddings
      - Personalized AI Re-ranking for highly accurate fashion recommendations.

Virtual Try-On Preview garments on user images using AI-based image overlay techniques.

### Fashion Chatbot Interactive AI assistant for: 
   - Styling advice
   - Trend suggestions
   - Outfit recommendations

### Trend Prediction Analyzes catalog data to identify:
- Trending categories
- Seasonal fashion patterns
- Rising outfit styles

### Smart Attribute Detection Detects:
- Clothing category
- Colors
- Patterns
- Style metadata

### Personalized Recommendation Engine Learns user preferences using: 
- Like/dislike feedback
- Embedding-based personalization
- Fashion similarity ranking

Voice Search Search fashion items using speech input.

Image Captioning Generate AI captions for uploaded fashion images.

### Multi-Modal Search Search using: 
- Text
- Image
- Combined text + image queries

Fashion Rating AI AI-generated outfit scoring system with aesthetic analysis.

## System Architecture

User Upload
↓
YOLO Fashion Detection
↓
Feature Extraction (FashionCLIP / AutoEncoder)
↓
Vector Embeddings
↓
FAISS / ChromaDB Similarity Search
↓
AI Recommendation Engine
↓
Frontend Display (React / Streamlit)

## Technologies Used 
- Frontend
    - React.js
    - Tailwind CSS
    - Framer Motion
    - Streamlit
- Backend
   - FastAPI
   - Python
- AI / Machine Learning
   - PyTorch
   - FashionCLIP
   - YOLOv5
   - OpenCV
   - Transformers
   - FAISS
   - ChromaDB
- Database & Search
   - ChromaDB
   - FAISS Vector Search

## Project Structure
SmartStylist/
│
├── home.py                         # Main Streamlit Application
├── obj_detection.py                # YOLO Fashion Object Detection
├── featurizer_model.py             # AutoEncoder Feature Extractor
├── migrate_to_fashionclip.py       # FashionCLIP Migration Script
├── embeddings.pkl                  # Stored Feature Embeddings
├── flatIndex.index                 # FAISS Similarity Search Index
├── img_paths.pkl                   # Dataset Image Paths
├── requirements.txt                # Python Dependencies
├── FULLSTACK.md                    # Full Stack Setup Guide
│
├── frontend/                       # React Frontend
├── backend/                        # FastAPI Backend
│
└── models/                         # Trained AI Models

### Installation
1️. Clone Repository git clone https://github.com/your-username/smart-stylist.git cd smart-stylist

2️. Create Virtual Environment Windows python -m venv venv venv\Scripts\activate Linux / Mac python3 -m venv venv source venv/bin/activate

3️. Install Dependencies pip install -r requirements.txt

Optional voice search support:

pip install -r requirements-optional.txt

 Running the Project
 - Streamlit App streamlit run home.py

App URL:

http://localhost:8501 🔹 Full Stack Application Run Backend .\run_backend.ps1 Run Frontend .\run_frontend.ps1 Or Run Everything .\run_all.ps1

Frontend:

http://localhost:5173

Backend API Docs:

http://127.0.0.1:8000/docs

3 AI Models Used Model Purpose YOLOv5 Fashion Object Detection FashionCLIP Fashion Embeddings AutoEncoder Feature Extraction BLIP Image Captioning ChromaDB Vector Storage FAISS Similarity Search

## Advanced Features

Real-time visual similarity search
Voice-enabled fashion retrieval
Personalized AI recommendations
AI trend forecasting
Multi-modal semantic search
Conversational fashion assistant
Fashion attribute recognition
AI outfit rating system
How It Works Fashion Search Pipeline User uploads an image YOLO detects fashion objects FashionCLIP extracts embeddings Embeddings are stored in vector DB Similarity search retrieves matching outfits AI ranks recommendation

## Dependencies Main libraries include:
- PyTorch
- Streamlit
- FastAPI
- OpenCV
- Transformers
- FAISS
- ChromaDB
- NumPy
- Pillow
- Scikit-learn

## Future Improvements
- 3D virtual try-on
- GAN-based outfit generation
- AI wardrobe planner
- Fashion marketplace integration
- Mobile application
- Real-time webcam fashion assistant
- Social outfit sharing platform

#### Author 
Renugha v

#### License 
This project is licensed under the Educational Purpose .
