import pandas as pd

def perform_merge(cluster_file_path, consumo_file_path):
    """
    Performs a left join from cluster_file_path to consumo_file_path,
    adding specified columns to the consumo DataFrame.

    Args:
        cluster_file_path (str): Path to the cluster data CSV.
        consumo_file_path (str): Path to the consumption data CSV.
    """
    # Load the cluster data
    # Assuming the reclassification script saved with comma and decimal as '.'
    df_cluster = pd.read_csv(cluster_file_path, sep=',', decimal='.')
    
    # Load the consumption data
    df_consumo = pd.read_csv(consumo_file_path, sep=',')

    # Ensure 'Aviario' in df_cluster is integer for merging
    df_cluster['Aviario'] = df_cluster['Aviario'].astype(int)

    # Select columns to merge from df_cluster
    columns_to_merge = ['Aviario', 'PontuacaoMax', 'IEPMedian', 'ClassifCluster', 'PerfilDescritivo']
    df_cluster_selected = df_cluster[columns_to_merge]

    # Perform the left merge
    # 'environmentName' in df_consumo corresponds to 'Aviario' in df_cluster
    df_merged = pd.merge(
        df_consumo,
        df_cluster_selected,
        left_on='environmentName',
        right_on='Aviario',
        how='left'
    )

    # Drop the redundant 'Aviario' column from the merged DataFrame
    df_merged.drop(columns=['Aviario'], inplace=True)

    # Save the updated DataFrame back to the consumption file
    df_merged.to_csv(consumo_file_path, sep=',', index=False, decimal='.')
    print(f"Merged data saved to '{consumo_file_path}' successfully.")

if __name__ == "__main__":
    cluster_csv_path = 'data/processed/cluster_aviarios_processado.csv'
    consumo_csv_path = 'data/processed/dataset_consumo_processed.csv'
    perform_merge(cluster_csv_path, consumo_csv_path)

