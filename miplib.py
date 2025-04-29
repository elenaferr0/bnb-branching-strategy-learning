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


def extract_zip(zip_file_path, extract_path):
    if os.path.exists(extract_path):
        print(f"Directory {extract_path} already exists. Skipping extraction.")
        return True

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
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

    # Take all the file names in df and create a zip file with them
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for index, row in df.iterrows():
            file_name = row['Instance']
            file_path = os.path.join(instances_path, file_name)
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=file_name)

def prepare_miplib_data():
    collection_url = "https://miplib.zib.de/downloads/collection.zip"
    benchmark_url = "https://miplib.zib.de/downloads/benchmark.zip"
    collection_zip_path = "dataset/collection.zip"
    benchmark_zip_path = "dataset/benchmark.zip"
    collection_extract_path = "dataset/collection"
    benchmark_extract_path = "dataset/benchmark"

    if not download_file(collection_url, collection_zip_path) or not extract_zip(collection_zip_path,
                                                                                 collection_extract_path):
        return
    # os.remove(collection_zip_path)

    if not download_file(benchmark_url, benchmark_zip_path) or not extract_zip(benchmark_zip_path,
                                                                               benchmark_extract_path):
        return
    # os.remove(benchmark_zip_path)

    collection_csv_path = os.path.join("dataset", "collection_set.csv")
    c = filter_easy_binary_problems(collection_csv_path)
    print(f"Found {len(c)} easy binary problems in collection set")
    create_filtered_instances_zip(c, collection_extract_path, "dataset/filtered_collection.zip")

    benchmark_csv_path = os.path.join("dataset", "benchmark_set.csv")
    b = filter_easy_binary_problems(benchmark_csv_path)
    print(f"Found {len(b)} easy binary problems in benchmark set")
    create_filtered_instances_zip(b, benchmark_extract_path, "dataset/filtered_benchmark.zip")


if __name__ == "__main__":
    prepare_miplib_data()
