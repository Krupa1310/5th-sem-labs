
import numpy as np
from PIL import Image
from pathlib import Path

width = 2048
height = 2048

project_dir = Path(__file__).resolve().parent
output_dir = project_dir / "output"

filters = ["3x3", "5x5", "7x7"]
implementations = ["naive", "constant", "shared"]

for implementation in implementations:
    for mask in filters:
        input_file = output_dir / f"{implementation}_{mask}.raw"
        output_file = output_dir / f"{implementation}_{mask}.png"

        data = np.fromfile(input_file, dtype=np.float32)
        image = data.reshape((height, width))

        image = np.clip(image, 0, 255).astype(np.uint8)

        Image.fromarray(image).save(str(output_file))

        print(f"Created: {output_file.name}")

print("\nAll CUDA output PNG images created successfully!")
