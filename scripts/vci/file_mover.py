import os
import shutil
from os.path import join

root = "/home/student_rohde/4K4D/data/vci_2024_12_12_dynamic"
source = "original_data/2024_12_12_dynamic2"
target = "scene_2"
camera_names = ["C0000", "C0001", "C0004", "C0005", "C0006", "C0007", "C0008", "C0010", "C0012", "C0013", "C0016", "C0018", "C0020", "C0024", "C0025", "C0026", "C0028", "C0029", "C0031", "C0034", "C0037", "C0038", "C0039", "C1000", "C1001", "C1004", "C1005"]
num_frames = 268
folder_per_camera = True

logging = False

def main():
    for _, dirs, files in os.walk(join(root, source)):
        
        if folder_per_camera:
            for cam in camera_names:
                os.makedirs(join(root, target, "images", cam), exist_ok=True)
                for folder in dirs:
                    if folder == "background":
                        continue
                    frame = "0" + folder[6:11] # frame_12345 -> 012345
                    source_file = join(source, folder, "rgb", cam + ".jpg")
                    target_file = join(target, "images", cam, frame + ".jpg")
                    copy_file(source_file, target_file)
        else:
            for folder in dirs:
                if folder == "background":
                    continue
                frame = "0" + folder[6:11] # frame_12345 -> 012345
                os.makedirs(join(root, target, "images", frame), exist_ok=True)
                for cam in camera_names:
                    source_file = join(source, folder, "rgb", cam + ".jpg")
                    target_file = join(target, "images", frame, cam + ".jpg")
                    copy_file(source_file, target_file)
            
        os.makedirs(join(root, target, "background"), exist_ok=True)
        for cam in camera_names:
            source_file = join(source, "background", "rgb", cam + ".jpg") 
            target_file = join(target, "background", cam + ".jpg")
            copy_file(source_file, target_file)
                    
        for file in files:
            source_file = join(source, file)
            target_file = join(target, file.replace(".json.json", ".json"))
            copy_file(source_file, target_file)

        break # to prevent walking into the folders
    
    print("\nDone!\n")
    
    
def copy_file(source_file, target_file):
    shutil.copy(join(root, source_file), join(root, target_file))
    if logging:
        print(f"Copied: (...)/{source_file} -> (...)/{target_file}")

if __name__ == "__main__":
    main()