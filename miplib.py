from pathlib import Path

import requests, gzip
import zipfile
import os
import pandas as pd
import shutil
from tqdm import tqdm


def download_file(url, local_filename, chunk_size=1024):
    if os.path.exists(local_filename):
        print(f"File {local_filename} already exists. Skipping download.")
        return True
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        with open(local_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    tqdm(total=total_size, unit='iB', unit_scale=True, desc=local_filename, ascii=True).update(
                        len(chunk))
        return total_size == 0 or file.tell() == total_size
    except requests.exceptions.RequestException:
        return False


def extract_zip(zip_file_path, extract_path=None):
    if extract_path is not None and os.path.exists(extract_path):
        print(f"Directory {extract_path} already exists. Skipping extraction.")
        return True

    try:
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path if extract_path else os.path.dirname(zip_file_path))
            return True
    except Exception as e:
        print(f"Error extracting {zip_file_path}: {e}")
        return False


def filter_easy_binary_problems(csv: str) -> pd.DataFrame:
    df = pd.read_csv(csv)
    filtered_df = df[(df['Integers'] == 0) & (df['Continuous'] == 0) & (df['Status'] == 'easy')]
    return filtered_df


def create_filtered_instances_zip(df: pd.DataFrame, instances_path: str, zip_path: str):
    if os.path.exists(zip_path):
        print(f"File {zip_path} already exists. Skipping creation.")
        return

    temp_dir = Path(zip_path).with_suffix(".tmp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    for i, row in df.iterrows():
        file = os.path.join(instances_path, f"{row['Instance']}.mps.gz")
        if os.path.exists(file):
            shutil.copy2(file, temp_dir)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname=arc_name)

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Created {zip_path} with {len(df)} instances of size {os.path.getsize(zip_path) / 1024.0}MB.")


def prepare_filtered_data(zip_url: str, zip_path: str, csv_path: str, filtered_zip_path: str):
    # if filtered zip already exists, skip download and load from it
    if os.path.exists(filtered_zip_path.replace(".zip", "")):
        print(f"Directory {filtered_zip_path.replace('.zip', '')} already exists. Skipping extraction.")
        return os.listdir(os.path.dirname(filtered_zip_path))

    if os.path.exists(filtered_zip_path):
        print(f"File {filtered_zip_path} already exists. Loading from it.")
        extract_zip(filtered_zip_path, filtered_zip_path.replace('.zip', ''))
        return os.listdir(os.path.dirname(filtered_zip_path))

    if not download_file(zip_url, zip_path) or not extract_zip(zip_path, os.path.dirname(zip_path)):
        return []

    # os.remove(zip_path)
    instances = filter_easy_binary_problems(csv_path)
    print(f"Found {len(instances)} easy binary problems in {csv_path}")

    # Re-zip instances for easier portability
    create_filtered_instances_zip(instances, zip_path.replace(".zip", ""), filtered_zip_path)
    return instances


def extract_gz(parent_path: str):
    print("Extracting gz files in " + parent_path)
    try:
        for root, _, files in os.walk(parent_path):
            for file in files:
                if not file.endswith('.gz'):
                    continue
                gz_path = os.path.join(root, file)
                with gzip.open(gz_path, 'rb') as f_in:
                    out_path = gz_path.replace('.gz', '')
                    with open(out_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(gz_path)
    except Exception as e:
        print(f"Error extracting gz files in {parent_path}: {e}")


def prepare_miplib_data():
    # collection is bigger and will be used for training (133 instances)
    collection_url = "https://miplib.zib.de/downloads/collection.zip"
    collection_zip_path = "dataset/collection.zip"
    collection_csv = "dataset/collection_set.csv"
    filtered_collection_zip_path = "dataset/filtered_collection.zip"
    prepare_filtered_data(collection_url, collection_zip_path, collection_csv,
                          filtered_collection_zip_path)
    extract_gz(filtered_collection_zip_path.replace(".zip", ""))

    # benchmark will be used for testing (39 instances)
    benchmark_url = "https://miplib.zib.de/downloads/benchmark.zip"
    benchmark_zip_path = "dataset/benchmark.zip"
    benchmark_csv = "dataset/benchmark_set.csv"
    filtered_benchmark_zip_path = "dataset/filtered_benchmark.zip"
    prepare_filtered_data(benchmark_url, benchmark_zip_path, benchmark_csv,
                          filtered_benchmark_zip_path)
    extract_gz(filtered_benchmark_zip_path.replace(".zip", ""))


if __name__ == "__main__":
    prepare_miplib_data()
