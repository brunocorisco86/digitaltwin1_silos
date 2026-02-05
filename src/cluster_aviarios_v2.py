import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Configuração de estilo
sns.set_theme(style="whitegrid")

def processar_analise_v2(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, sep=';', decimal=',', names=['Aviario', 'PontuacaoMax', 'IEPMedian'], header=0).dropna()
    
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df[['PontuacaoMax', 'IEPMedian']])
    
    # K=5 conforme solicitado
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    df['Cluster_Eficiencia'] = kmeans.fit_predict(df_scaled)
    
    # Centroides
    centroids_scaled = kmeans.cluster_centers_
    centroids = scaler.inverse_transform(centroids_scaled)
    
    # Resumo
    resumo = df.groupby('Cluster_Eficiencia').agg({
        'PontuacaoMax': 'mean',
        'IEPMedian': 'mean',
        'Aviario': 'count'
    }).rename(columns={'Aviario': 'Quantidade'}).reset_index()
    
    resumo['Centroid_X'] = centroids[:, 0]
    resumo['Centroid_Y'] = centroids[:, 1]
    
    # Médias globais para quadrantes
    m_pont = df['PontuacaoMax'].mean()
    m_iep = df['IEPMedian'].mean()
    
    # Definição de perfis para 5 clusters
    # Como temos 5, um cluster provavelmente será "Intermediário" ou "Transição"
    def rotular_perfil(row):
        px, iep = row['PontuacaoMax'], row['IEPMedian']
        if px >= m_pont and iep >= m_iep:
            return "Alta Performance Top"
        elif px < m_pont and iep >= m_iep:
            return "Manejo de Ouro"
        elif px >= m_pont and iep < m_iep:
            if px > 85: return "Subutilizado Premium"
            return "Subutilizado Padrão"
        else:
            if px < 30: return "Crítico Severo"
            return "Crítico em Transição"

    resumo['Perfil'] = resumo.apply(rotular_perfil, axis=1)
    mapeamento = dict(zip(resumo['Cluster_Eficiencia'], resumo['Perfil']))
    df['Perfil_Descritivo'] = df['Cluster_Eficiencia'].map(mapeamento)
    
    return df, resumo, m_pont, m_iep

def plotar_v2(df, resumo, m_pont, m_iep):
    plt.figure(figsize=(14, 9))
    
    # Scatter plot
    sns.scatterplot(
        data=df, x='PontuacaoMax', y='IEPMedian', hue='Perfil_Descritivo',
        palette='Set1', s=70, alpha=0.5, edgecolor='none'
    )
    
    # Centroides
    plt.scatter(
        resumo['Centroid_X'], resumo['Centroid_Y'], 
        c='black', s=250, marker='*', label='Centroides (K=5)',
        edgecolor='white', linewidth=1.5, zorder=10
    )
    
    # Anotações
    for _, row in resumo.iterrows():
        plt.annotate(
            row['Perfil'], (row['Centroid_X'], row['Centroid_Y']),
            textcoords="offset points", xytext=(0,10), ha='center',
            fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.6)
        )
        
    plt.axvline(m_pont, color='gray', linestyle='--', alpha=0.6)
    plt.axhline(m_iep, color='gray', linestyle='--', alpha=0.6)
    
    plt.title('Clusterização C.Vale (K=5) com Centroides e Validação', fontsize=15)
    plt.xlabel('Pontuação Estrutural')
    plt.ylabel('IEP Mediana')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/cluster_v2_k5.png')
    plt.close()

if __name__ == "__main__":
    df, res, mp, mi = processar_analise_v2("/home/ubuntu/upload/dataset_iep_pontuacao.csv")
    df.to_csv('/home/ubuntu/dataset_aviarios_k5.csv', index=False, sep=';')
    plotar_v2(df, res, mp, mi)
    print(res.to_string())
