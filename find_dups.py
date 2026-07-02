import os
import shutil
import hashlib
import argparse
from pathlib import Path

def get_file_hash(filepath, chunk_size=8192):
    """Calculates the SHA-256 hash of a file's contents."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_and_move_duplicates(target_dir):
    target_path = Path(target_dir).resolve()
    
    if not target_path.is_dir():
        print(f"Error: The directory '{target_dir}' does not exist.")
        return

    # Create the 'duplicates' folder inside the target directory
    duplicates_folder = target_path / "duplicates"
    duplicates_folder.mkdir(exist_ok=True)

    seen_hashes = {}
    moved_count = 0

    print(f"Scanning '{target_path}' for duplicates...\n")

    # Walk through the directory tree recursively
    for root, dirs, files in os.walk(target_path):
        # Prevent the script from scanning the new 'duplicates' folder
        if duplicates_folder.name in dirs and Path(root) == target_path:
            dirs.remove(duplicates_folder.name)

        for filename in files:
            filepath = Path(root) / filename
            
            try:
                # Generate a unique fingerprint (hash) for the file's content
                file_hash = get_file_hash(filepath)
                
                if file_hash in seen_hashes:
                    original_file = seen_hashes[file_hash]
                    print(f"Duplicate detected:\n  Original: {original_file}\n  Duplicate: {filepath}")
                    
                    dest_path = duplicates_folder / filename
                    counter = 1
                    while dest_path.exists():
                        dest_path = duplicates_folder / f"{filepath.stem}_{counter}{filepath.suffix}"
                        counter += 1
                        
                    print(f"  Moving to -> {dest_path}\n")
                    shutil.move(str(filepath), str(dest_path))
                    moved_count += 1
                else:
                    seen_hashes[file_hash] = filepath
                    
            except PermissionError:
                print(f"Skipped (Permission Denied): {filepath}")
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    print("---")
    print(f"Finished! Successfully moved {moved_count} duplicate file(s) to '{duplicates_folder}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan a directory for duplicate files and move them to a 'duplicates' folder.")
    parser.add_argument("directory", help="The path to the directory you want to scan.")
    args = parser.parse_args()
    
    find_and_move_duplicates(args.directory)

