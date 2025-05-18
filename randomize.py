import pandas as pd
import numpy as np
from scipy import stats
import argparse
import os

def perturb_dataset(file_path, output_path=None, min_factor=0.001, max_factor=1.0, seed=None):
    """
    Read a pickle file and apply random perturbations to each feature.
    Each feature gets a different random perturbation factor between min_factor and max_factor.
    """
    # Set random seed if provided
    if seed is not None:
        np.random.seed(seed)

    # Read the pickle file
    print(f"Reading data from {file_path}")
    df = pd.read_pickle(file_path)

    # Create a copy for modifications
    df_modified = df.copy()

    # Store statistics and perturbation factors
    stats_dict = {}
    perturbation_factors = {}

    # Get list of columns to perturb (all except 'score')
    feature_columns = [col for col in df.columns if col != 'score']

    # Generate random perturbation factors for each feature
    for column in feature_columns:
        perturbation_factors[column] = np.random.uniform(min_factor, max_factor)

    # Process each column
    for column in feature_columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            # Compute statistics
            col_stats = {
                'mean': df[column].mean(),
                'std': df[column].std(),
                'min': df[column].min(),
                'max': df[column].max(),
            }

            # Apply perturbation based on column-specific factor
            factor = perturbation_factors[column]
            noise_amount = col_stats['std'] * factor
            noise = np.random.normal(0, noise_amount, size=len(df))
            df_modified[column] = df[column] + noise

            # Store the used perturbation factor
            col_stats['perturbation_factor'] = factor
            col_stats['perturbation_amount'] = noise_amount
            stats_dict[column] = col_stats

    # Save modified DataFrame if output path is provided
    if output_path:
        print(f"Saving modified data to {output_path}")
        df_modified.to_pickle(output_path)

    # Print summary of modifications
    print("\nPerturbation Summary:")
    for column, s in stats_dict.items():
        print(f"{column}: factor={s['perturbation_factor']:.5f}, "
              f"amount={s['perturbation_amount']:.5g}, "
              f"mean={s['mean']:.5g}, std={s['std']:.5g}")

    return df, df_modified, stats_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perturb features in dataset with random factors.")
    parser.add_argument("input_file", help="Path to input pickle file")
    parser.add_argument("-o", "--output", help="Path to save modified data")
    parser.add_argument("--min", type=float, default=0.001, help="Minimum perturbation factor")
    parser.add_argument("--max", type=float, default=1.0, help="Maximum perturbation factor")
    parser.add_argument("-s", "--seed", type=int, help="Random seed")

    args = parser.parse_args()

    # Generate output path if not specified
    if args.output is None:
        base, ext = os.path.splitext(args.input_file)
        args.output = f"{base}_perturbed{ext}"

    # Run the perturbation
    _, _, _ = perturb_dataset(
        args.input_file,
        args.output,
        args.min,
        args.max,
        args.seed
    )

    print("Done!")
