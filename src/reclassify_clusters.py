import pandas as pd

def reclassify_clusters(file_path):
    """
    Reclassifies the 'Cluster_Eficiencia' column in a CSV file.
    The reclassification is done in ascending order, starting from 0,
    based on the 'IEP_Median' values, grouped by 'Perfil_Descritivo'.

    Args:
        file_path (str): The path to the CSV file.
    """
    # Read the CSV file
    df = pd.read_csv(file_path, sep=';', decimal=',')
    df['IEPMedian'] = pd.to_numeric(df['IEPMedian'], errors='coerce') # Convert to numeric, coerce errors will turn invalid parsing into NaN
    df.dropna(subset=['IEPMedian'], inplace=True) # Drop rows where IEPMedian could not be converted

    # Group by 'Perfil_Descritivo' and reclassify 'Cluster_Eficiencia' based on 'IEP_Median'
    # Calculate the mean 'IEPMedian' for each 'Perfil_Descritivo'
    mean_iep_by_perfil = df.groupby('Perfil_Descritivo')['IEPMedian'].mean().sort_values().reset_index()

    # Create a mapping for new 'Cluster_Eficiencia' based on sorted mean 'IEPMedian'
    # The new cluster values will be 0, 1, 2, 3... based on the rank of their mean IEPMedian
    perfil_to_new_cluster = {perfil: i for i, perfil in enumerate(mean_iep_by_perfil['Perfil_Descritivo'].tolist())}

    # Apply the new mapping to the 'Cluster_Eficiencia' column
    df['Cluster_Eficiencia'] = df['Perfil_Descritivo'].map(perfil_to_new_cluster)

    # Save the modified DataFrame back to the CSV file
    df.to_csv(file_path, sep=';', decimal=',', index=False)
    print(f"File '{file_path}' reclassified successfully.")

if __name__ == "__main__":
    csv_file_path = 'data/processed/cluster_aviarios_processado.csv'
    reclassify_clusters(csv_file_path)
