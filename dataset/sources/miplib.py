from pathlib import Path

import requests, gzip
import zipfile
import os
import pandas as pd
import shutil
from tqdm import tqdm
from pysmps import smps_loader as smps

from dataset.solver import Problem


def __download_file(url, local_filename, chunk_size=1024):
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


def __extract_zip(zip_file_path, extract_path=None):
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


def __filter_instances(csv: str) -> pd.DataFrame:
    df = pd.read_csv(csv)
    filtered_df = df[(df['Integers'] == 0) & (df['Continuous'] == 0) & (df['Binaries'] <= 500) & (df['Constraints'] < 5000)]
    return filtered_df


def __create_filtered_instances_zip(df: pd.DataFrame, instances_path: str, zip_path: str):
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
        files = os.listdir(temp_dir)
        for file in tqdm(files, desc="Creating filtered files zip"):
            file_path = os.path.join(temp_dir, file)
            arc_name = os.path.relpath(file_path, temp_dir)
            zipf.write(file_path, arcname=arc_name)

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Created {zip_path} with {len(df)} instances of size {os.path.getsize(zip_path) / 1024.0}MB.")


def __prepare_filtered_data(zip_url: str, zip_path: str, csv_path: str, filtered_zip_path: str):
    # if filtered zip already exists, skip download and load from it
    filtered_dir = filtered_zip_path.replace(".zip", "")
    if os.path.exists(filtered_dir) and len(os.listdir(filtered_dir)) > 0:
        print(f"Directory {filtered_dir} already exists. Skipping extraction.")
        return os.listdir(filtered_dir)

    if os.path.exists(filtered_zip_path):
        print(f"File {filtered_zip_path} already exists. Loading from it.")
        __extract_zip(filtered_zip_path, filtered_zip_path.replace('.zip', ''))
        return os.listdir(filtered_dir)

    if not __download_file(zip_url, zip_path) or not __extract_zip(zip_path, os.path.dirname(zip_path)):
        return []

    # os.remove(zip_path)
    instances = __filter_instances(csv_path)
    print(f"Found {len(instances)} easy binary problems in {csv_path}")

    # Re-zip instances for easier portability
    __create_filtered_instances_zip(instances, zip_path.replace(".zip", ""), filtered_zip_path)
    return list(map(lambda x: f"{x}.mps", instances['Instance'].tolist()))


def __extract_gz(parent_path: str):
    try:
        files = os.listdir(parent_path)
        for file in tqdm(files, desc="Extracting gz files"):
            if not file.endswith('.gz'):
                continue
            gz_path = os.path.join(parent_path, file)
            out_path = gz_path.replace('.gz', '')
            with gzip.open(gz_path, 'rb') as f_in, open(out_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(gz_path)
        print("Extracted gz files in " + parent_path)
    except Exception as e:
        print(f"Error extracting gz files in {parent_path}: {e}")


def load_mps(path: str):
    name, _, _, _, _, types, c, A, rhs_names, rhs, _, _ = smps.load_mps(path)
    return Problem(
        name=name,
        c=c,
        lb=[0] * len(c),
        ub=[1] * len(c),
        types=types,
        b=rhs[rhs_names[0]],
        A=A,
    )


def load_miplib_dataset(size_limit=None):
    url = "https://miplib.zib.de/downloads/collection.zip"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(current_dir, "miplib/collection.zip")
    csv = os.path.join(current_dir, "miplib/collection_set.csv")
    filtered_path = os.path.join(current_dir, "miplib/filtered_collection")
    instances = __prepare_filtered_data(url, zip_path, csv, f"{filtered_path}.zip")
    if size_limit is not None:
        instances = instances[:size_limit]
    __extract_gz(filtered_path)
    return [load_mps(f"{filtered_path}/{i}") for i in tqdm(instances, desc="Loading mps files")]