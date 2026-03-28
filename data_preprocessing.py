import os
import numpy as np
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
from sklearn.model_selection import train_test_split
import pickle

# Initialize MediaPipe Hand Landmarker (new API)
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Download the hand landmarker model
import urllib.request
MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading MediaPipe hand landmarker model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        MODEL_PATH
    )
    print("Model downloaded! ✅")

DATASET_PATH = "asl_alphabet_train/asl_alphabet_train"

def extract_landmarks(image_path):
    """Extract hand landmarks from an image"""
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.3
    )
    
    with HandLandmarker.create_from_options(options) as landmarker:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb
        )
        
        results = landmarker.detect(mp_image)
        
        if results.hand_landmarks:
            landmarks = []
            for landmark in results.hand_landmarks[0]:
                landmarks.extend([landmark.x, landmark.y, landmark.z])
            return landmarks
    return None

def load_dataset():
    """Load dataset and extract landmarks"""
    data = []
    labels = []
    classes = sorted(os.listdir(DATASET_PATH))
    
    print(f"Found {len(classes)} classes: {classes}")
    
    # Create landmarker once for efficiency
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.3
    )
    
    with HandLandmarker.create_from_options(options) as landmarker:
        for label_idx, class_name in enumerate(classes):
            class_path = os.path.join(DATASET_PATH, class_name)
            if not os.path.isdir(class_path):
                continue
            
            images = os.listdir(class_path)[:500]
            print(f"Processing {class_name} ({label_idx+1}/{len(classes)})...")
            
            count = 0
            for image_name in images:
                image_path = os.path.join(class_path, image_name)
                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=image_rgb
                )
                
                results = landmarker.detect(mp_image)
                
                if results.hand_landmarks:
                    landmarks = []
                    for landmark in results.hand_landmarks[0]:
                        landmarks.extend([landmark.x, landmark.y, landmark.z])
                    data.append(landmarks)
                    labels.append(label_idx)
                    count += 1
            
            print(f"  → {count} valid images processed")
    
    return np.array(data), np.array(labels), classes

def preprocess_and_save():
    """Main function to process and save data"""
    print("Starting data preprocessing...")
    print("This may take 20-30 minutes. Please wait...\n")
    
    data, labels, classes = load_dataset()
    
    print(f"\nTotal samples collected: {len(data)}")
    print(f"Total classes: {len(classes)}")
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        data, labels,
        test_size=0.2,
        random_state=42,
        stratify=labels
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Save everything to disk
    with open("preprocessed_data.pkl", "wb") as f:
        pickle.dump({
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "classes": classes
        }, f)
    
    print("\nData saved to preprocessed_data.pkl ✅")
    print("Preprocessing complete! ✅")

if __name__ == "__main__":
    preprocess_and_save()