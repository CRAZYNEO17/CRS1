import os
import shutil

# Create data directories
data_dir = os.path.join(os.path.dirname(__file__), 'data')
raw_dir = os.path.join(data_dir, 'raw')
processed_dir = os.path.join(data_dir, 'processed')

os.makedirs(raw_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

# Files to move to raw data
raw_files = [
    'crop_data.csv',
    'agricultural_schemes.json',
]

# Files to move to processed data
processed_files = [
    'weather_cache.json',
    'location_data.json'
]

# Move files to raw directory
for file in raw_files:
    src = os.path.join(os.path.dirname(__file__), file)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(raw_dir, file))
        print(f"Copied {file} to raw data directory")

# Move files to processed directory 
for file in processed_files:
    src = os.path.join(os.path.dirname(__file__), file)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(processed_dir, file))
        print(f"Copied {file} to processed data directory")

# Move model files to processed directory
models_dir = os.path.join(os.path.dirname(__file__), 'models')
if os.path.exists(models_dir):
    target_models_dir = os.path.join(processed_dir, 'models')
    if not os.path.exists(target_models_dir):
        os.makedirs(target_models_dir)
    for file in os.listdir(models_dir):
        shutil.copy2(os.path.join(models_dir, file), os.path.join(target_models_dir, file))
    print("Copied models directory to processed data directory")

print("Data organization complete!")