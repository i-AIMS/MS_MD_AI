import argparse
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_path')
    args = parser.parse_args()

    # Read PubMed results
    df = pd.read_csv('PubMed_results_2026-07-26.csv')

    # Calculate number of publications since 2016
    n_total = df['Count'].sum()
    n_last_decase = df['Count'][df['Year'] >= 2016].sum()
    print(f'{n_last_decase} of {n_total} in last decade ({n_last_decase/n_total*100:.2f}%)')

    # Create figure
    fig, ax = plt.subplots()
    ax.plot(df['Year'], df['Count'])
    ax.set_xlabel('Year')
    ax.set_ylabel('Count')
    plt.savefig(args.output_path, dpi=300)
