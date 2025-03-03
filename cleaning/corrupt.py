import os
from PIL import Image

def remove_corrupted_images(folder_path):
    """
    Scans a folder and removes corrupted images.
    
    :param folder_path: Path to the folder containing images.
    """
    corrupted_files = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify if image is not corrupted
        except (IOError, SyntaxError):
            corrupted_files.append(file_path)
            os.remove(file_path)
            print(f"❌ Removed corrupted image: {file_path}")

    if not corrupted_files:
        print("✅ No corrupted images found!")
    else:
        print(f"🗑️ Removed {len(corrupted_files)} corrupted images.")

# Example usage
remove_corrupted_images(r"D:\oral_cancer_detection\data\cancer")
