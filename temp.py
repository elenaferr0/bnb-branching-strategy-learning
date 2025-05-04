from dataset.generator import generate_datasets

if __name__ == '__main__':
    ds = generate_datasets(1, 1, 1, 1)
    print(ds[0])
