import os
import sys
from PIL import Image
import imagehash

def get_image_files(folder_path):
    """Get all image files from a folder."""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    image_files = []
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in image_extensions:
                image_files.append(file_path)
    
    return image_files

def compute_image_hash(image_path):
    """Compute hash for an image."""
    try:
        img = Image.open(image_path)
        hash_value = imagehash.phash(img)
        return hash_value
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def remove_duplicate_images(source_folder, target_folder):
    """
    Compare images in source_folder with target_folder and remove duplicates from target_folder.
    """
    print(f"Scanning source folder: {source_folder}")
    source_images = get_image_files(source_folder)
    print(f"Found {len(source_images)} images in source folder")
    
    print(f"Scanning target folder: {target_folder}")
    target_images = get_image_files(target_folder)
    print(f"Found {len(target_images)} images in target folder")
    
    # Compute hashes for source images
    source_hashes = {}
    for img_path in source_images:
        hash_value = compute_image_hash(img_path)
        if hash_value is not None:
            source_hashes[img_path] = hash_value
    
    # Track removed files
    removed_count = 0
    
    # Compare target images with source images
    for target_img in target_images:
        target_hash = compute_image_hash(target_img)
        if target_hash is None:
            continue
        
        # Check if this image is a duplicate of any source image
        for source_img, source_hash in source_hashes.items():
            # Check if hashes match
            if target_hash == source_hash:
                # Remove the duplicate image from target folder
                print(f"Removing duplicate: {os.path.basename(target_img)}")
                os.remove(target_img)
                removed_count += 1
                break
    
    print(f"\nTotal duplicates removed: {removed_count}")

def main():
    source_folder = r"D:\oral_cancer_detection\data\non_cancer"
    target_folder = r"D:\oral_cancer_detection\testdata\non_cancer"
    
    if not os.path.isdir(source_folder):
        print(f"Error: Source folder '{source_folder}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(target_folder):
        print(f"Error: Target folder '{target_folder}' does not exist.")
        sys.exit(1)
    
    remove_duplicate_images(source_folder, target_folder)

if __name__ == "__main__":
    main()