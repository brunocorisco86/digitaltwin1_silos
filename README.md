# Gêmeo Digital de Consumo de Ração em Silos

## 1. Visão Geral do Projeto

Este projeto desenvolve um **Gêmeo Digital** para estimar a taxa de esvaziamento de silos em aviários que não possuem sensores físicos. Utilizando um modelo de Machine Learning (Random Forest Regressor), o sistema prevê o consumo de ração por ave por dia (`feed_measuredPerBird`) para cada `batchAge` (idade do lote) e `Aviario`. O objetivo é otimizar a logística, melhorar o monitoramento e promover o bem-estar animal, integrando dados zootécnicos e estruturais.

O projeto gera previsões suavizadas de consumo, e diversas visualizações para analisar o comportamento da ração, incluindo curvas de consumo por cluster, boxplots de distribuição por idade e gráficos da mediana de consumo agrupados por cluster e por faixas de pontuação máxima (`PontuacaoMax`).

## 2. Pipeline de Análise e Previsão

O pipeline de dados e análise é projetado para processar dados brutos, treinar um modelo preditivo e gerar visualizações e relatórios. Para detalhes técnicos completos sobre a preparação de dados, critérios de filtragem, premissas e o fluxo de execução, consulte o documento de conhecimento detalhado: [`knowledge/consumption_prediction_process.md`](knowledge/consumption_prediction_process.md).

### 2.1. Preparação e Filtragem de Dados

A fase de preparação envolve a limpeza e transformação rigorosa dos dados. Para garantir a qualidade dos dados para o treinamento do modelo, foram aplicadas filtragens baseadas em:
*   **`confidence_level`**: Somente registros com `confidence_level >= 0.8` são considerados, focando em medições de alta fidelidade.
*   **`IEPMedian`**: Outliers são removidos, mantendo valores de `IEPMedian` entre 200 e 500 para mitigar o impacto de problemas sanitários atípicos.
*   Mais detalhes sobre as regras de filtragem podem ser encontrados em [`knowledge/consumption_prediction_process.md`](knowledge/consumption_prediction_process.md).

### 2.2. Features e Variável Alvo

O modelo foi treinado para prever `feed_measuredPerBird`. As principais features utilizadas são:
*   `AreaAlojamento_Encoded`
*   `batchAge`
*   `ClassifCluster`
*   `PontuacaoMax`
*   `IEPMedian`

### 2.3. Modelo e Avaliação de Desempenho

Um modelo `RandomForestRegressor` foi utilizado com sucesso para prever o consumo. Sua robustez foi confirmada através de validação cruzada e avaliação por clusters.

*   **Validação Cruzada (K-Fold)**: O modelo alcançou um **Mean Absolute Error (MAE) médio de 14.78 (+/- 0.75)**. Este resultado indica a boa capacidade de generalização do modelo em dados não vistos.
*   **Importância das Features**: A análise de importância das features revelou que `batchAge` é a variável mais influente na previsão do consumo. O ranking completo das features é:
    | Feature                |   Importance |
    |:-----------------------|-------------:|
    | batchAge               |    0.943345  |
    | IEPMedian              |    0.0263203 |
    | AreaAlojamento_Encoded |    0.0145208 |
    | PontuacaoMax           |    0.0103588 |
    | ClassifCluster         |    0.0054555 |
*   **Métrica de Erro (MAE) por Cluster**: A avaliação segmentada por clusters mostrou as seguintes performances:
    | Cluster          |     MAE |
    |:-----------------|--------:|
    | Críticos         |  4.0091 |
    | Alta Performance |  7.9977 |
    | Manejo de Ouro   | 10.3162 |
    | Subutilizados    | 10.6978 |
    Para mais detalhes sobre as métricas, consulte: [`reports/report.md`](reports/report.md).

### 2.4. Geração de Previsões e Visualizações

O pipeline gera previsões suavizadas e uma série de gráficos para análise aprofundada:
*   **Curvas de Consumo Suavizadas (Global)**: `images/plots/smoothed_consumption_curves_per_aviario.png`
*   **Curvas de Consumo Suavizadas (Por Cluster)**: `images/plots/smoothed_consumption_curves_<Nome_do_Cluster>.png` (e.g., para 'Manejo de Ouro', 'Subutilizados', 'Críticos', 'Alta Performance')
*   **Boxplot de Consumo por Idade do Lote**: `images/plots/consumption_boxplot_per_batchage.png`
*   **Mediana do Consumo por Idade do Lote e Cluster**: `images/plots/median_consumption_by_batchage_per_cluster.png`
*   **Mediana do Consumo por Idade do Lote e Grupo de Pontuação Máxima**: `images/plots/median_consumption_by_batchage_per_pontuacaomax_bin.png`

## 3. Estrutura do Projeto

O projeto é organizado em módulos Python para modularidade e reusabilidade:

*   **`main.py`**: (Atualmente não utilizado para o fluxo de ML) Pode ser refatorado para orquestrar o pipeline completo.
*   **`src/analyze_silo_data.py`**: Contém a lógica para treinar o modelo `RandomForestRegressor`, extrair importância das features e realizar a avaliação por cluster e validação cruzada.
*   **`src/predict_consumption.py`**: Gera as previsões de consumo de ração com base no modelo treinado, aplica suavização e salva os resultados.
*   **`src/plot_consumption_curves.py`**: Gera as curvas de consumo suavizadas (globais e por cluster).
*   **`src/plot_consumption_boxplot.py`**: Gera boxplots da distribuição do consumo por idade do lote.
*   **`src/plot_median_consumption_by_cluster.py`**: Gera gráficos de linha da mediana de consumo por idade do lote e cluster.
*   **`src/plot_median_consumption_by_pontuacaomax_bins.py`**: Gera gráficos de linha da mediana de consumo por idade do lote e grupos de `PontuacaoMax`.
*   **`data/processed/predicted_consumption_per_bird.csv`**: Arquivo CSV principal contendo as previsões de consumo.
*   **`images/plots/`**: Diretório onde todos os gráficos gerados são salvos.
*   **`reports/report.md`**: Relatório detalhado do desempenho do modelo, métricas e validação cruzada.
*   **`reports/feature_importances.md`**: Ranking de importância das features do modelo.
*   **`knowledge/consumption_prediction_process.md`**: Documentação técnica aprofundada do pipeline.

## 4. Tech Stack

*   **Linguagem**: Python 3.10+
*   **Ambiente Dev**: Pop_OS! / Windows 11 (com Docker)
*   **Bibliotecas Core**:
    *   `pandas` & `numpy`: Manipulação de dados.
    *   `scikit-learn`: Modelagem (RandomForestRegressor), Métricas (MAE, R²).
    *   `matplotlib` & `seaborn`: Visualização de dados.
    *   `tabulate`: Geração de tabelas formatadas em Markdown.
    *   `pydantic`: Validação de modelos de dados (utilizado na fase de ETL inicial, embora não diretamente nos scripts de ML atuais).
*   **Ambiente Virtual**: `.venv`

## 5. Como Executar

Para replicar os resultados ou gerar novas análises:

1.  **Garanta o ambiente virtual**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2.  **Instale as dependências**:
    ```bash
    .venv/bin/python3 -m pip install -r requirements.txt
    ```
3.  **Execute os scripts de análise e visualização**:
    Para gerar as previsões e os plots, execute os seguintes scripts na ordem:
    ```bash
    .venv/bin/python3 src/predict_consumption.py
    .venv/bin/python3 src/plot_consumption_curves.py
    .venv/bin/python3 src/plot_consumption_boxplot.py
    .venv/bin/python3 src/plot_median_consumption_by_cluster.py
    .venv/bin/python3 src/plot_median_consumption_by_pontuacaomax_bins.py
    ```
    Os relatórios de texto (`reports/report.md` e `reports/feature_importances.md`) são gerados como parte da execução de `predict_consumption.py` (via `analyze_silo_data.py`).

---