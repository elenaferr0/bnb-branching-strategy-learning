import requests
import zipfile
import os
import pandas as pd
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


def extract_zip(zip_file_path, extract_path = None):
    if extract_path is not None and os.path.exists(extract_path):
        print(f"Directory {extract_path} already exists. Skipping extraction.")
        return True

    try:
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print(os.path.dirname(zip_file_path))
            zip_ref.extractall(extract_path if extract_path else os.path.dirname(zip_file_path))
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

    # Take all the file names in df and create a zip file with them
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for index, row in df.iterrows():
            file_name = row['Instance']
            file_path = os.path.join(instances_path, file_name)
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=file_name)
    print(f"Created {zip_path} with {len(df)} instances of size {os.path.getsize(zip_path)} bytes.")

def prepare_data(zip_url: str, zip_path: str, csv_path: str, filtered_zip_path: str):
    # if filtered zip already exists, skip download and load from it
    if os.path.exists(filtered_zip_path):
        print(f"File {filtered_zip_path} already exists. Loading from it.")
        extract_zip(filtered_zip_path, filtered_zip_path.replace('.zip', ''))
        return os.listdir(os.path.dirname(filtered_zip_path))

    if (not download_file(zip_url, zip_path) or not extract_zip(zip_path, os.path.dirname(zip_path))):
        return

    # os.remove(zip_path)
    instances = filter_easy_binary_problems(csv_path)
    print(f"Found {len(instances)} easy binary problems in {csv_path}")

    # Re-zip instances for easier portability
    create_filtered_instances_zip(instances, os.path.dirname(zip_path), filtered_zip_path)
    return instances


def prepare_miplib_data():
    # collection is bigger and will be used for training (133 instances)
    collection_url = "https://miplib.zib.de/downloads/collection.zip"
    collection_zip_path = "dataset/collection.zip"
    collection_csv = "dataset/collection_set.csv"
    filtered_collection_zip_path = "dataset/filtered_collection.zip"
    collection_instances = prepare_data(collection_url, collection_zip_path, collection_csv, filtered_collection_zip_path)

    # benchmark will be used for testing (39 instances)
    benchmark_url = "https://miplib.zib.de/downloads/benchmark.zip"
    benchmark_zip_path = "dataset/benchmark.zip"
    benchmark_csv = "dataset/benchmark_set.csv"
    filtered_benchmark_zip_path = "dataset/filtered_benchmark.zip"
    benchmark_instances = prepare_data(benchmark_url, benchmark_zip_path, benchmark_csv, filtered_benchmark_zip_path)


if __name__ == "__main__":
    prepare_miplib_data()
