import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def plot_median_consumption_by_cluster(input_file, output_dir):
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

    # Calculate the median consumption per batchAge per PerfilDescritivo
    median_consumption = df.groupby(['batchAge', 'PerfilDescritivo'])['smoothed_feed_measuredPerBird'].median().reset_index()

    # Set up the plot style
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(15, 8))

    # Create the line plot
    sns.lineplot(
        data=median_consumption,
        x='batchAge',
        y='smoothed_feed_measuredPerBird',
        hue='PerfilDescritivo',
        marker='o' # Add markers for each data point
    )

    plt.title('Mediana do Consumo de Ração Suavizado por Idade do Lote e Cluster')
    plt.xlabel('Idade do Lote (batchAge)')
    plt.ylabel('Mediana do Consumo Predito e Suavizado por Ave')
    plt.xticks(range(int(median_consumption['batchAge'].min()), int(median_consumption['batchAge'].max()) + 1, 5)) # Set x-ticks for better readability
    plt.legend(title='Perfil Descritivo', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Save the plot
    output_path = os.path.join(output_dir, 'median_consumption_by_batchage_per_cluster.png')
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to '{output_path}'")

if __name__ == "__main__":
    current_dir = os.getcwd()
    
    input_csv_file = os.path.join(current_dir, 'data', 'processed', 'predicted_consumption_per_bird.csv')
    output_plots_dir = os.path.join(current_dir, 'images', 'plots')
    
    plot_median_consumption_by_cluster(input_csv_file, output_plots_dir)