# Processo de Previsão de Consumo de Ração por Ave por Dia (feed_measuredPerBird)

Este documento detalha o pipeline completo para a previsão do consumo de ração por ave por dia (`feed_measuredPerBird`) em aviários, utilizando um modelo Random Forest Regressor.

## 1. Objetivo do Projeto

Estimar a taxa de esvaziamento de silos para aviários que não possuem sensores físicos, fornecendo uma previsão de `feed_measuredPerBird` para cada idade (`batchAge`) e aviário (`Aviario`).

## 2. Dados Utilizados

*   **`data/processed/dataset_consumo_processed.csv`**: Dataset principal para treinamento do modelo. Contém informações detalhadas de consumo, níveis de confiança e características dos aviários.
*   **`data/processed/cluster_aviarios_encoded.csv`**: Dataset contendo informações de aviários, utilizado para gerar a base para as previsões.

## 3. Pipeline de Execução

### 3.1. Filtragem de Qualidade

Para garantir que o modelo aprendesse com dados de alta fidelidade e evitar ruídos, as seguintes filtragens foram aplicadas ao `dataset_consumo_processed.csv`:

*   **`confidence_level`**: Apenas registros com `confidence_level >= 0.8` foram utilizados. Este limiar foi definido para focar nas medições mais confiáveis, representando o "riscado central" das curvas de consumo.
*   **`IEPMedian`**: Outliers foram removidos, excluindo valores de `IEPMedian` fora do intervalo de 200 a 500. Isso visou mitigar o impacto de problemas sanitários atípicos nos dados.

### 3.2. Preparação de Features (X) e Target (Y) para Treinamento

O modelo foi treinado para prever `feed_measuredPerBird`. As seguintes features foram selecionadas:

*   **`AreaAlojamento_Encoded`**: Representação numérica codificada da área de alojamento.
*   **`batchAge`**: Idade do lote, que foi re-incluída como uma feature crítica para a previsão do consumo diário.
*   **`ClassifCluster`**: Identificador numérico do cluster de aviário (0: Críticos, 1: Subutilizados, 2: Manejo de Ouro, 3: Alta Performance).
*   **`PontuacaoMax`**: Pontuação máxima do aviário.
*   **`IEPMedian`**: Mediana do Índice de Eficiência Produtiva (IEP).

Identificadores como `environmentName`, `clientName` e `loteComposto` foram ignorados no treinamento. Linhas com valores `NaN` nas colunas de features, target ou `confidence_level` foram removidas.

### 3.3. Treinamento do Modelo (Machine Learning)

*   **Modelo**: Um `RandomForestRegressor` foi instanciado com 100 árvores (`n_estimators=100`) e `random_state=42` para reprodutibilidade.
*   **Pesos (`sample_weight`)**: A coluna `confidence_level` foi utilizada como peso no treinamento (`sample_weight`), conferindo maior importância aos dados com maior fidelidade e confiança.

### 3.4. Validação Cruzada (Cross-validation)

Para avaliar a capacidade de generalização do modelo e obter uma estimativa mais robusta do seu desempenho, foi aplicada uma validação cruzada K-Fold (com 5 folds, embaralhamento e `random_state=42`). O Mean Absolute Error (MAE) médio e o desvio padrão foram calculados através dos folds.

*   **MAE Médio (Cross-validation)**: 14.78
*   **Desvio Padrão do MAE (Cross-validation)**: 0.75

Estes resultados indicam a performance esperada do modelo em dados não vistos, conferindo a confiança de que os resultados estão funcionando como esperado.

### 3.5. Extração de Importância das Features

Após o treinamento, o `feature_importances_` do modelo foi extraído para determinar o peso relativo de cada variável na previsão do consumo. Este ranking pode ser encontrado no relatório `reports/feature_importances.md`.

### 3.6. Geração de Previsões de Consumo por Aviário e Idade

Para gerar as previsões, um novo dataset foi construído com base em `cluster_aviarios_encoded.csv`:

*   **Dataset Base**: `cluster_aviarios_encoded.csv` foi carregado, fornecendo `Aviario`, `PontuacaoMax`, `IEPMedian`, `ClassifCluster` e `AreaAlojamento_Encoded`.
*   **Combinações `Aviario`-`batchAge`**: Para cada `Aviario` único no dataset `cluster_aviarios_encoded.csv`, foram geradas combinações com `batchAge` variando de 1 a 48 dias.
*   **Montagem do Dataset de Previsão**: As informações de `PontuacaoMax`, `IEPMedian`, `ClassifCluster` e `AreaAlojamento_Encoded` foram mescladas com as combinações `Aviario`-`batchAge`.
*   **Previsões**: O modelo `RandomForestRegressor` treinado foi utilizado para prever `feed_measuredPerBird` para cada entrada no dataset de previsão gerado.
*   **Arredondamento**: Os valores de `predicted_feed_measuredPerBird` foram arredondados para 0 casas decimais.

### 3.8. Saída dos Resultados

*   **Previsões**: As previsões de `predicted_feed_measuredPerBird` (arredondadas), juntamente com o `Aviario` e `batchAge` correspondentes, foram salvas no arquivo `data/processed/predicted_consumption_per_bird.csv`. Este arquivo agora inclui informações detalhadas do cluster como `PontuacaoMax`, `IEPMedian`, `ClassifCluster`, `PerfilDescritivo` e `AreaAlojamento`.
*   **Curvas de Consumo Suavizadas (Global)**: Um gráfico das curvas de consumo suavizadas (`smoothed_feed_measuredPerBird` em função de `batchAge` por aviário, com legenda por `PerfilDescritivo`) foi salvo em `images/plots/smoothed_consumption_curves_per_aviario.png`.
*   **Curvas de Consumo Suavizadas (Por Cluster)**: Gráficos individuais das curvas de consumo suavizadas foram gerados para cada cluster (`Manejo de Ouro`, `Subutilizados`, `Críticos`, `Alta Performance`), salvos em `images/plots/smoothed_consumption_curves_<Nome_do_Cluster>.png`.
*   **Boxplot de Consumo por Idade do Lote**: Um boxplot do `Consumo Predito e Suavizado por Ave` por `Idade do Lote (batchAge)` foi salvo em `images/plots/consumption_boxplot_per_batchage.png`. Este gráfico permite visualizar a distribuição e a variabilidade do consumo para cada idade.
*   **Mediana do Consumo por Idade do Lote e Cluster**: Um gráfico de linha mostrando a mediana do `Consumo Predito e Suavizado por Ave` por `batchAge`, segregado por `PerfilDescritivo` (cluster), foi salvo em `images/plots/median_consumption_by_batchage_per_cluster.png`. Este plot permite comparar a tendência central de consumo entre os diferentes clusters ao longo do tempo.
*   **Mediana do Consumo por Idade do Lote e Grupo de Pontuação Máxima**: Um gráfico de linha mostrando a mediana do `Consumo Predito e Suavizado por Ave` por `batchAge`, segregado por grupos de `PontuacaoMax` (0-20, 21-40, etc.), foi salvo em `images/plots/median_consumption_by_batchage_per_pontuacaomax_bin.png`. Este plot permite comparar a tendência central de consumo entre diferentes faixas de pontuação máxima ao longo do tempo.
*   **Relatório de Treinamento**: Um relatório detalhado do treinamento do modelo, incluindo as métricas MAE por cluster, o ranking de importância das variáveis e os resultados da validação cruzada, foi salvo em `reports/report.md`.
*   **Importância das Features**: A tabela de importância das features foi salva separadamente em `reports/feature_importances.md`.

## 5. Avaliação por Cluster

O erro médio absoluto (MAE) foi calculado segregadamente para cada um dos clusters (Críticos, Subutilizados, Manejo de Ouro, Alta Performance) para validar a precisão do Gêmeo Digital em diferentes perfis de manejo. Os resultados estão disponíveis em `reports/report.md`.
