import os
from PIL import Image
import imagehash
from collections import defaultdict

def find_duplicates(image_folder):
    """
    Find duplicate images in a folder using perceptual hashing.

    Args:
        image_folder (str): Path to the folder containing images.

    Returns:
        list: A list of duplicate image groups.
    """
    hashes = defaultdict(list)

    # Iterate through all images in the folder
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff',".PNG")):
            filepath = os.path.join(image_folder, filename)
            try:
                with Image.open(filepath) as img:
                    # Generate a perceptual hash (e.g., average hash)
                    img_hash = imagehash.average_hash(img)
                    hashes[img_hash].append(filepath)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Identify duplicate groups (images with the same hash)
    duplicates = [files for files in hashes.values() if len(files) > 1]
    return duplicates

def remove_duplicates(duplicates):
    """
    Remove duplicate images, keeping only one copy of each.

    Args:
        duplicates (list): A list of duplicate image groups.
    """
    for duplicate_group in duplicates:
        # Keep the first image in the group and delete the rest
        for duplicate in duplicate_group[1:]:
            os.remove(duplicate)
            print(f"Removed {duplicate}")

def main(image_folder):
    """
    Main function to find and remove duplicate images.

    Args:
        image_folder (str): Path to the folder containing images.
    """
    # Find duplicates
    duplicates = find_duplicates(image_folder)
    print(f"Found {len(duplicates)} groups of duplicates.")

    # Remove duplicates
    remove_duplicates(duplicates)
    print("Duplicate removal complete.")

# Example usage
image_folder = r"D:\oral_cancer_detection\testdata\non_cancer"
main(image_folder)