import os
import shutil
import datetime
from PIL import Image

def organize_photos(source_dir, dest_dir, batch_size=100):
    """
    Organizes photos from a source directory into a destination directory,
    grouping them by year and month. It processes photos in batches.
    Handles duplicate filenames by appending a counter.

    Args:
        source_dir (str): The directory containing the photos to organize.
        dest_dir (str): The directory where the organized photos will be stored.
        batch_size (int): The number of photos to process in each batch.
    """

    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    photos = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    num_photos = len(photos)
    
    print(f"Found {num_photos} photos to organize.")

    for i in range(0, num_photos, batch_size):
        batch = photos[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}: Photos {i+1} to {min(i + batch_size, num_photos)}")

        for photo in batch:
            photo_path = os.path.join(source_dir, photo)
            try:
                img = Image.open(photo_path)
                exif_data = img._getexif()

                if exif_data and 36867 in exif_data:
                    date_taken_str = exif_data[36867]  # DateTimeOriginal tag
                    date_taken = datetime.datetime.strptime(date_taken_str, '%Y:%m:%d %H:%M:%S')
                else:
                    # If EXIF data is missing, use file modification time
                    file_info = os.stat(photo_path)
                    date_taken = datetime.datetime.fromtimestamp(file_info.st_mtime)

                year = str(date_taken.year)
                month = str(date_taken.month).zfill(2)  # Pad with zero if needed

                year_dir = os.path.join(dest_dir, year)
                if not os.path.exists(year_dir):
                    os.makedirs(year_dir)

                month_dir = os.path.join(year_dir, month)
                if not os.path.exists(month_dir):
                    os.makedirs(month_dir)

                dest_path = os.path.join(month_dir, photo)
                
                # Handle duplicate filenames
                name, ext = os.path.splitext(dest_path)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = f"{name}_{counter}{ext}"
                    counter += 1
                    
                shutil.copy2(photo_path, dest_path)  # copy2 preserves metadata
                print(f"Moved '{photo}' to '{dest_path}'")

            except Exception as e:
                print(f"Error processing '{photo}': {e}")

if __name__ == '__main__':
    source_directory = 'source_photos'  # Replace with your source directory
    destination_directory = 'organized_photos'  # Replace with your destination directory
    organize_photos(source_directory, destination_directory, batch_size=100)
    print("Photo organization complete.")
