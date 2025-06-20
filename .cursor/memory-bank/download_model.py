from sentence_transformers import SentenceTransformer
import os

model_name = 'all-MiniLM-L6-v2'
# The cache dir will be inside the project structure.
# The script will be run from the project root.
cache_dir = os.path.join('.cursor', 'memory-bank', 'models')

print(f"Downloading {model_name} to {cache_dir}...")

# This will download the model to the specified cache directory.
# The library will create a sentence-transformers cache folder inside this path.
model = SentenceTransformer(model_name, cache_folder=cache_dir)

print("Model downloaded successfully.") 