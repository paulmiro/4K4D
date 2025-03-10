import json
import yaml
import sys
import os
import numpy as np
import cv2
from os.path import join, exists
import re
import shutil

default_input_file_name = "calibration.json"

camera_names = ["C0000", "C0001", "C0004", "C0005", "C0006", "C0007", "C0008", "C0010", "C0012", "C0013", "C0016", "C0018", "C0020", "C0024", "C0025", "C0026", "C0028", "C0029", "C0031", "C0034", "C0037", "C0038", "C0039", "C1000", "C1001", "C1004", "C1005"]

def main():
    if len(sys.argv) < 2:
        print("Usage: python calibration_converter.py <directory_path> [<calibration_file_name>]")
        sys.exit(1)
    
    if len(sys.argv) > 2:
        input_file_name = sys.argv[2]
    else:
        input_file_name = default_input_file_name
    
    directory_path = sys.argv[1]

    input_file = os.path.join(directory_path, input_file_name)
    output_extri_file = os.path.join(directory_path, "extri.yml")
    output_intri_file = os.path.join(directory_path, "intri.yml")

    if not os.path.exists(input_file):
        print(f"Error: The input file '{input_file}' does not exist.")
        sys.exit(1)

    data = read_json(input_file)

    (extri, intri) = convert(data)

    write_yaml(extri, output_extri_file)
    write_yaml(intri, output_intri_file)
    
    fixup(directory_path)

    print(
        f"Data successfully converted and written to \n{output_extri_file}\n{output_intri_file}"
    )


def convert(data):
    cameras = data["cameras"]

    extri = {}
    intri = {}

    camera_ids = []

    for camera in cameras:
        name = camera["camera_id"]
        if name not in camera_names:
            continue

        camera_ids = camera_ids + [name]

        vm = np.array(camera["extrinsics"]["view_matrix"]).reshape(4, 4)

        Rot = vm[0:3, 0:3]
        R, _ = cv2.Rodrigues(Rot)
        T = vm[0:3, 3:4]

        extri[f"Rot_{name}"] = {"rows": 3, "cols": 3, "dt": "d"}
        extri[f"Rot_{name}"]["data"] = Rot.flatten().tolist()

        extri[f"R_{name}"] = {"rows": 3, "cols": 1, "dt": "d"}
        extri[f"R_{name}"]["data"] = R.flatten().tolist()

        extri[f"T_{name}"] = {"rows": 3, "cols": 1, "dt": "d"}
        extri[f"T_{name}"]["data"] = T.flatten().tolist()

        intri[f"K_{name}"] = {"rows": 3, "cols": 3, "dt": "d"}
        intri[f"K_{name}"]["data"] = camera["intrinsics"]["camera_matrix"]

        intri[f"ccm_{name}"] = {"rows": 3, "cols": 3, "dt": "d"}
        intri[f"ccm_{name}"]["data"] = camera["intrinsics"]["color_correction_matrix"]

        intri[f"D_{name}"] = {"rows": 5, "cols": 1, "dt": "d"}
        intri[f"D_{name}"]["data"] = camera["intrinsics"]["distortion_coefficients"]

        intri[f"W_{name}"] = camera["intrinsics"]["resolution"][0]
        intri[f"H_{name}"] = camera["intrinsics"]["resolution"][1]

    extri["names"] = camera_ids
    intri["names"] = camera_ids

    return (extri, intri)

def fixup(directory_path):
    extri_file = join(directory_path, "extri.yml")
    intri_file = join(directory_path, "intri.yml")

    if not exists(extri_file):
        print(f"Error: The input file '{extri_file}' does not exist.")
        sys.exit(1)
        
    if not exists(intri_file):
        print(f"Error: The input file '{intri_file}' does not exist.")
        sys.exit(1)
        
    extri, intri = "", ""

    with open(extri_file, "r") as file:
        extri = file.read()
    with open(intri_file, "r") as file:
        intri = file.read()
    
    
    intri = re.sub(
        "D_C(\\d+):\\n  cols: 1\\n  data:(?:\\n  - -?\\d+.\\d+(?:e-\\d+)?){5}\\n  dt: d\\n  rows: 5",
        "D_C\\1:\\n  cols: 1\\n  data:\\n  - 0.0\\n  - 0.0\\n  - 0.0\\n  - 0.0\\n  - 0.0\\n  dt: d\\n  rows: 5",
        intri
    )
    
    tags = ["Rot", "R", "T", "K", "ccm", "D" ] # H and W are not opencv-matrix
    for tag in tags:
        extri = re.sub(f"({tag}_C[0-9]+:)", "\\1 !!opencv-matrix", extri)
        intri = re.sub(f"({tag}_C[0-9]+:)", "\\1 !!opencv-matrix", intri)
    
    extri = re.sub("\\n(\\s*-\\s)","\\n  \\1", extri)
    intri = re.sub("\\n(\\s*-\\s)","\\n  \\1", intri)


    intri = "%YAML:1.0\n---\n" + intri
    extri = "%YAML:1.0\n---\n" + extri

    with open(extri_file, "w") as file:
        file.write(extri)
    with open(intri_file, "w") as file:
        file.write(intri)


def read_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def write_yaml(data, file_path):
    with open(file_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


if __name__ == "__main__":
    main()
