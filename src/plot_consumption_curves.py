import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def plot_consumption_curves(input_file, output_dir):
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
    plt.figure(figsize=(15, 10))

    # Get unique descriptive profiles
    perfil_descritivo_names = df['PerfilDescritivo'].unique()

    # Iterate through each unique descriptive profile to create separate plots
    for perfil_name in perfil_descritivo_names:
        cluster_df = df[df['PerfilDescritivo'] == perfil_name].copy()

        # Set up a new figure for each cluster
        plt.figure(figsize=(15, 10))
        sns.set_theme(style="whitegrid")

        # Get unique Aviarios within this cluster for plotting individual curves
        unique_aviarios_in_cluster = cluster_df['Aviario'].unique()
        
        # Define a single color for all curves within this cluster plot for consistency
        # Or, if we want different shades for different aviarios within a cluster, we can use a palette
        # For now, let's just use one color or slightly varied shades if possible.
        # Let's use a subtle palette for Aviarios within the same cluster.
        aviario_colors = sns.color_palette("viridis", len(unique_aviarios_in_cluster))
        aviario_color_map = dict(zip(unique_aviarios_in_cluster, aviario_colors))


        # Plot consumption curve for each Aviario in the current cluster
        for aviario, aviario_df in cluster_df.groupby('Aviario'):
            plt.plot(
                aviario_df['batchAge'],
                aviario_df['smoothed_feed_measuredPerBird'],
                color=aviario_color_map.get(aviario, 'gray'),
                alpha=0.6,
                linewidth=1,
                label=f"Aviario {aviario}" # Label each aviario for a potential legend
            )
        
        # Add a legend for aviarios within the cluster if desired, but for clarity, let's omit it for now
        # plt.legend(title="Aviários", bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.title(f'Curvas de Consumo de Ração Suavizadas para o Cluster: {perfil_name}')
        plt.xlabel('Idade do Lote (batchAge)')
        plt.ylabel('Consumo Predito e Suavizado por Ave (smoothed_feed_measuredPerBird)')
        plt.tight_layout()

        # Sanitize perfil_name for use in filename
        sanitized_perfil_name = perfil_name.replace(" ", "_").replace("/", "_")
        output_path = os.path.join(output_dir, f'smoothed_consumption_curves_{sanitized_perfil_name}.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Plot saved to '{output_path}'")


if __name__ == "__main__":
    current_dir = os.getcwd()
    
    input_csv_file = os.path.join(current_dir, 'data', 'processed', 'predicted_consumption_per_bird.csv')
    output_plots_dir = os.path.join(current_dir, 'images', 'plots')
    
    plot_consumption_curves(input_csv_file, output_plots_dir)
