from PIL import Image
import os

# Ensure AVIF support
try:
    import pillow_avif
except ImportError:
    print("⚠️ AVIF support missing. Install with: pip install pillow-avif-plugin")

def convert_images_to_jpeg(image_folder):
    """
    Convert all images in a folder to JPEG format and delete the originals,
    including WEBP and AVIF images.

    Args:
        image_folder (str): Path to the folder containing images.
    """
    # Supported image formats including WEBP and AVIF
    supported_formats = ('.png', '.bmp', '.tiff', '.webp', '.gif', '.avif')  

    # Iterate through all files in the folder
    for filename in os.listdir(image_folder):
        filepath = os.path.join(image_folder, filename)
        
        # Skip already JPEG images
        if filename.lower().endswith(('.jpg', '.jpeg')):
            continue  

        if filename.lower().endswith(supported_formats):
            try:
                with Image.open(filepath) as img:
                    # Convert to RGB mode (JPEG doesn't support alpha channel)
                    rgb_img = img.convert("RGB")

                    # Create new filename with .jpg extension
                    new_filename = os.path.splitext(filename)[0] + ".jpg"
                    new_filepath = os.path.join(image_folder, new_filename)

                    # Save the image in JPEG format
                    rgb_img.save(new_filepath, "JPEG")
                    print(f"✅ Converted {filename} → {new_filename}")

                    # Delete the original image
                    os.remove(filepath)
                    print(f"🗑️ Deleted original file: {filename}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

    print("🎯 All non-JPEG images converted and originals deleted successfully!")

# Example usage
image_folder = r"D:\oral_cancer_detection\testdata\non_cancer"
convert_images_to_jpeg(image_folder)
