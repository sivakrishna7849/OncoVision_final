import os

def rename_images_to_sequential(folder_path, start_number=1):
    """
    Renames all images in a folder to sequential numbers like 001, 002, etc.,
    starting from a custom number.

    Args:
        folder_path (str): Path to the folder containing images.
        start_number (int): The starting number for renaming (default is 1).
    """
    # Get a list of all image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif',".PNG"))]
    image_files.sort()  # Sort files alphabetically (optional)

    # Rename files sequentially starting from the custom number
    for index, filename in enumerate(image_files, start=start_number):
        # Get the file extension
        _, ext = os.path.splitext(filename)

        # Create the new filename (e.g., 100.jpg, 101.png)
        new_filename = f"{index:03}{ext}"  # Zero-padded 3-digit number

        # Get full paths for old and new filenames
        old_filepath = os.path.join(folder_path, filename)
        new_filepath = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(old_filepath, new_filepath)
        print(f"Renamed: {filename} -> {new_filename}")

    print("All images renamed successfully!")

# Example usage
folder_path = r"D:\oral_cancer_detection\testdata\non_cancer"
start_number = 1
  # Start renaming from 100
rename_images_to_sequential(folder_path, start_number)