import pandas as pd
import numpy as np

def gerar_estatistica(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, sep=';', decimal=',', names=['Aviario', 'PontuacaoMax', 'IEPMedian'], header=0).dropna()
    
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df[['PontuacaoMax', 'IEPMedian']])
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(df_scaled)
    
    # Estatística Descritiva por Cluster
    stats = df.groupby('Cluster').agg({
        'PontuacaoMax': ['mean', 'std', 'min', 'max'],
        'IEPMedian': ['mean', 'std', 'min', 'max', 'median'],
        'Aviario': 'count'
    }).reset_index()
    
    # Nomear os clusters baseado nos perfis anteriores para facilitar o storytelling
    # Cluster 0: Subutilizados, Cluster 1: Alta Performance, Cluster 2: Manejo de Ouro, Cluster 3: Críticos
    perfis = {0: 'Subutilizados', 1: 'Alta Performance', 2: 'Manejo de Ouro', 3: 'Críticos'}
    stats['Perfil'] = stats['Cluster'].map(perfis)
    
    return stats, df

if __name__ == "__main__":
    stats, df_final = gerar_estatistica("/home/ubuntu/upload/dataset_iep_pontuacao.csv")
    print(stats.to_string())
    df_final.to_csv('/home/ubuntu/dataset_final_4clusters.csv', index=False, sep=';')
