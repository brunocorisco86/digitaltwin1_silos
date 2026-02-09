import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def plot_consumption_boxplot(input_file, output_dir):
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: The input file '{input_file}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading the CSV file: {e}")
        sys.exit(1)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Set up the plot style
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 10)) # Adjust figure size for better readability

    # Create the boxplot
    sns.boxplot(
        data=df,
        x='batchAge',
        y='smoothed_feed_measuredPerBird',
        palette='viridis' # Choose a color palette
    )

    plt.title('Boxplot do Consumo de Ração Suavizado por Idade do Lote (batchAge)')
    plt.xlabel('Idade do Lote (batchAge)')
    plt.ylabel('Consumo Predito e Suavizado por Ave (smoothed_feed_measuredPerBird)')
    plt.xticks(rotation=45) # Rotate x-axis labels if they overlap
    plt.tight_layout()

    # Save the plot
    output_path = os.path.join(output_dir, 'consumption_boxplot_per_batchage.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Boxplot saved to '{output_path}'")

if __name__ == "__main__":
    current_dir = os.getcwd()
    
    input_csv_file = os.path.join(current_dir, 'data', 'processed', 'predicted_consumption_per_bird.csv')
    output_plots_dir = os.path.join(current_dir, 'images', 'plots')
    
    plot_consumption_boxplot(input_csv_file, output_plots_dir)