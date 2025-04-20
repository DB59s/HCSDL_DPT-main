import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
import cv2
from mountain_feature_extractor import extract_features, calculate_euclidean_distance
import pymongo
import argparse
from pymongo.errors import ConnectionFailure
from datetime import datetime
import json

# Cập nhật URI MongoDB Atlas mặc định
DEFAULT_MONGODB_URI = "mongodb+srv://vuduy050903:JggOWW4dggxdA5IE@cluster0.rowvk9i.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def normalize_features(features, max_length=None):
    """Normalize features to have consistent dimensions."""
    # If max_length is not provided, just return the original features
    if max_length is None:
        return features
    
    # If features are too long, truncate them
    if len(features) > max_length:
        return features[:max_length]
    
    # If features are too short, pad with zeros
    if len(features) < max_length:
        padded = np.zeros(max_length)
        padded[:len(features)] = features
        return padded
    
    # If the length is already correct, return as is
    return features

def get_features_from_mongodb(mongodb_uri=None):
    """Retrieve features from MongoDB database."""
    if mongodb_uri is None:
        mongodb_uri = DEFAULT_MONGODB_URI
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(mongodb_uri)
        db = client["mountain_image_search"]
        collection = db["image_features"]
        
        print(f"Connected to MongoDB Atlas")
        
        # Retrieve all image features
        cursor = collection.find({})
        
        # Construct features dictionary
        features_dict = {}
        for doc in cursor:
            image_name = doc["image_name"]
            features = doc["features"]
            features_dict[image_name] = np.array(features)
        
        print(f"Retrieved features for {len(features_dict)} images from MongoDB")
        return features_dict
    
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Error retrieving data from MongoDB: {e}")
        return None

def find_similar_images(query_image_path, features_dict=None, mongodb_uri=None, top_n=3, use_mongodb=True):
    """Find the top N most similar images to the query image using Euclidean distance."""
    # Extract features from the query image
    query_features = extract_features(query_image_path)
    
    # Get features from MongoDB if requested
    if use_mongodb and features_dict is None:
        features_dict = get_features_from_mongodb(mongodb_uri)
        
        # If MongoDB retrieval failed, try to load from pickle
        if features_dict is None:
            print("Falling back to local pickle file...")
            try:
                with open("mountain_features.pkl", "rb") as f:
                    features_dict = pickle.load(f)
                print(f"Loaded features for {len(features_dict)} images from pickle file")
            except Exception as e:
                print(f"Failed to load features from pickle: {e}")
                return []
    
    # If still no features, return empty list
    if not features_dict:
        print("No features available for comparison")
        return []
    
    # Find the most common feature vector length in the database
    lengths = [len(features) for features in features_dict.values()]
    common_length = np.bincount(lengths).argmax() if lengths else len(query_features)
    
    print(f"Query feature length: {len(query_features)}, Common length in database: {common_length}")
    
    # Normalize query features to common length
    normalized_query_features = normalize_features(query_features, common_length)
    
    # Calculate distances to all images in the database
    distances = {}
    for image_name, features in features_dict.items():
        # Normalize features to common length
        normalized_features = normalize_features(features, common_length)
        
        # Calculate Euclidean distance
        distance = np.sqrt(np.sum((normalized_query_features - normalized_features) ** 2))
        distances[image_name] = distance
    
    # Sort by distance (smaller distance means more similar)
    sorted_images = sorted(distances.items(), key=lambda x: x[1])
    
    # Return top N similar images (excluding the query image if it's in the database)
    query_image_name = os.path.basename(query_image_path)
    
    # Save search result to MongoDB
    if use_mongodb:
        save_search_result_to_mongodb(query_image_path, sorted_images[:top_n], mongodb_uri)
    
    return [img for img in sorted_images if img[0] != query_image_name][:top_n]

def save_search_result_to_mongodb(query_image_path, similar_images, mongodb_uri=None):
    """Save search results to MongoDB for analytics."""
    if mongodb_uri is None:
        mongodb_uri = DEFAULT_MONGODB_URI
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(mongodb_uri)
        db = client["mountain_image_search"]
        collection = db["search_history"]
        
        # Prepare document
        query_image_name = os.path.basename(query_image_path)
        result = {
            "query_image": query_image_name,
            "query_path": query_image_path,
            "timestamp": datetime.now(),
            "results": [
                {"image_name": img_name, "similarity_score": float(distance)}
                for img_name, distance in similar_images
            ]
        }
        
        # Insert document
        collection.insert_one(result)
        print(f"Search result saved to MongoDB")
        
    except Exception as e:
        print(f"Error saving search result to MongoDB: {e}")

def visualize_similar_images(query_image_path, similar_images, image_dir, output_dir="similarity_results"):
    """Visualize the query image and its most similar matches."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the base name of the query image for the output filename
    query_base_name = os.path.splitext(os.path.basename(query_image_path))[0]
    
    # Create a figure with multiple subplots
    plt.figure(figsize=(15, 8))
    
    # Display query image
    query_image = cv2.imread(query_image_path)
    query_image_rgb = cv2.cvtColor(query_image, cv2.COLOR_BGR2RGB)
    plt.subplot(1, 4, 1)
    plt.imshow(query_image_rgb)
    plt.title("Query Image")
    plt.axis('off')
    
    # Display similar images
    for i, (image_name, distance) in enumerate(similar_images):
        # Read and display the similar image
        image_path = os.path.join(image_dir, image_name)
        similar_image = cv2.imread(image_path)
        similar_image_rgb = cv2.cvtColor(similar_image, cv2.COLOR_BGR2RGB)
        
        plt.subplot(1, 4, i+2)
        plt.imshow(similar_image_rgb)
        plt.title(f"Rank {i+1}: {image_name}\nDistance: {distance:.2f}")
        plt.axis('off')
    
    # Save the visualization
    plt.tight_layout()
    output_path = os.path.join(output_dir, f"{query_base_name}_similar.jpg")
    plt.savefig(output_path)
    plt.close()
    
    print(f"Similarity visualization saved to {output_path}")
    
    return output_path

def export_results_to_json(query_image_path, similar_images, output_dir="similarity_results"):
    """Export search results to a JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the base name of the query image for the output filename
    query_base_name = os.path.splitext(os.path.basename(query_image_path))[0]
    
    # Prepare results
    results = {
        "query_image": os.path.basename(query_image_path),
        "query_path": query_image_path,
        "timestamp": datetime.now().isoformat(),
        "results": [
            {"rank": i+1, "image_name": img_name, "similarity_score": float(distance)}
            for i, (img_name, distance) in enumerate(similar_images)
        ]
    }
    
    # Save to JSON
    output_path = os.path.join(output_dir, f"{query_base_name}_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results exported to {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find similar mountain images")
    parser.add_argument("query_image", help="Path to the query image")
    parser.add_argument("--image_dir", default="../mountain_images", help="Directory containing all images")
    parser.add_argument("--features_file", default="mountain_features.pkl", help="Path to the features file (used as fallback if MongoDB fails)")
    parser.add_argument("--mongodb_uri", default=DEFAULT_MONGODB_URI, help="MongoDB connection URI")
    parser.add_argument("--no_mongodb", action="store_true", help="Don't use MongoDB, use local pickle file instead")
    parser.add_argument("--top_n", type=int, default=3, help="Number of similar images to find")
    parser.add_argument("--export_json", action="store_true", help="Export results to JSON file")
    
    args = parser.parse_args()
    
    # Get features from file if not using MongoDB
    features_dict = None
    if args.no_mongodb:
        try:
            with open(args.features_file, "rb") as f:
                features_dict = pickle.load(f)
            print(f"Loaded features for {len(features_dict)} images from {args.features_file}")
        except Exception as e:
            print(f"Error loading features from {args.features_file}: {e}")
            print("Will try to use MongoDB instead.")
    
    # Find similar images
    similar_images = find_similar_images(
        args.query_image, 
        features_dict, 
        args.mongodb_uri, 
        args.top_n,
        use_mongodb=not args.no_mongodb
    )
    
    if not similar_images:
        print("No similar images found")
        exit(1)
    
    # Display results
    print(f"\nTop {args.top_n} similar images to {args.query_image}:")
    for i, (image_name, distance) in enumerate(similar_images):
        print(f"{i+1}. {image_name} - Distance: {distance:.4f}")
    
    # Visualize results
    output_path = visualize_similar_images(args.query_image, similar_images, args.image_dir)
    
    # Export to JSON if requested
    if args.export_json:
        json_path = export_results_to_json(args.query_image, similar_images) 