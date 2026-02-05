# Análise e ETL para Gêmeo Digital de Consumo de Ração em Silos

## 1. Visão Geral do Projeto

Este projeto tem como objetivo principal a análise e o processamento de dados para o desenvolvimento de um **Gêmeo Digital** focado na estimativa da taxa de esvaziamento de silos em aviários. Utilizando técnicas de Machine Learning, o sistema visa converter dados zootécnicos e estruturais em previsões de estoque, otimizando a logística e promovendo o bem-estar animal, conforme a visão geral da base de conhecimento do Projeto AgroCenter (C.Vale).

## 2. Pipeline de Dados (Foco do Desenvolvimento Atual: ETL)

O desenvolvimento atual concentra-se na fase de **Processamento & Feature Engineering**, especificamente na construção de um pipeline de ETL (Extração, Transformação e Carga) robusto para dados de consumo de ração.

### Fases do Pipeline ETL Implementado:

1.  **Extração de Dados Brutos (`DataExtractor`)**:
    *   **Origem**: Arquivos JSON brutos localizados em `/data/raw/`, nomeados no padrão `AVIARIO XXX - Lote YYY - GUID.json`.
    *   **Processo**: Os JSONs são lidos e parseados utilizando modelos Pydantic (`src/data_model.py`) e um carregador dedicado (`src/utils/data_loader.py`).
    *   **Resultado**: Consolidação dos dados relevantes (e.g., `environmentName`, `batchName`, `batchAge`, `feed_measuredPerBird`) em um DataFrame inicial.

2.  **Processamento e Filtragem Inicial (`ETLProcessor`)**:
    *   **Limpeza e Transformação**:
        *   Remoção dos prefixos "AVIARIO " de `environmentName` e "Lote " de `batchName`, convertendo-os para inteiros.
        *   Criação da coluna `loteComposto` (concatenação de `environmentName` e `batchName`, e posicionada como a terceira coluna).
    *   **Filtragem por `feed_measuredPerBird`**: Manutenção apenas de registros onde `feed_measuredPerBird` está entre **15 e 250 (inclusive)**.
    *   **Filtragem por Contagem de `loteComposto`**: Lotes compostos com **menos de 15 registros** após o filtro de `feed_measuredPerBird` são descartados.

3.  **Filtragem por Comportamento Inicial/Final de Consumo (`ETLProcessor`)**:
    *   **Critério**: Lotes compostos são mantidos se o `feed_measuredPerBird` na **idade mínima do lote** estiver entre **0 e 50**, E o `feed_measuredPerBird` na **idade máxima do lote** estiver entre **150 e 250**. Lotes que não atendem a ambos os critérios são removidos.

4.  **Modelagem da Curva e Cálculo de Confiança (`CurveModeler`)**:
    *   **Curva de Consumo**: Para cada `loteComposto`, uma regressão polinomial de grau 2 é ajustada para modelar a relação entre `feed_measuredPerBird` e `batchAge`.
    *   **Nível de Confiança**: O Coeficiente de Determinação ($R^2$) do modelo ajustado é calculado e adicionado como uma coluna `confidence_level` ao dataset.

5.  **Filtragem por Nível de Confiança ($R^2$) (`ETLProcessor`)**:
    *   **Critério**: Lotes compostos são mantidos apenas se o seu `confidence_level` (R²) for **maior ou igual a 0.80**.

6.  **Agregação do Consumo por Ave (`Aggregator`)**:
    *   **Processo**: Calcula-se o somatório total de `feed_measuredPerBird` para cada `loteComposto`, agregando o consumo por ave ao longo de todas as idades do lote.
    *   **Resultado**: O resultado é salvo em um novo arquivo `aggregated_consumption_per_bird.csv` em `/data/processed/`.

7.  **Salvamento dos Dados Processados (`ETLProcessor`)**:
    *   O DataFrame final, após todas as etapas de filtragem e enriquecimento, é salvo em `/data/processed/dataset_consumo_processed.csv`.

8.  **Geração de Visualização (`Plotter`)**:
    *   **Gráfico**: Gera um plot das curvas de consumo (`feed_measuredPerBird` vs `batchAge`) para os `loteComposto`s que sobreviveram aos filtros.
    *   **Coloração**: As curvas são coloridas com base no `confidence_level` (R²):
        *   `< 0.90`: Vermelho
        *   `0.90 <= R² < 0.95`: Verde
        *   `0.95 <= R² < 1.00`: Azul
        *   `R² = 1.00`: Roxo (ou aproximadamente 1.00)
    *   **Suavização**: As curvas são suavizadas através de regressão polinomial (grau 2).
    *   **Legenda**: Inclui legendas apenas para os níveis de confiança.
    *   **Local**: O plot é salvo em `/images/plots/curvas_consumo_new.png`.

## 3. Estrutura Orientada a Objetos (OOP)

O pipeline foi refatorado para uma estrutura orientada a objetos (OOP) para melhorar a modularidade, reusabilidade e manutenção do código.

*   **`main.py`**: Orquestra todo o fluxo, sequenciando as etapas de Extração, Processamento/Filtragem, Modelagem e Geração de Plots.
*   **`src/data_extractor.py` (`DataExtractor`)**: Responsável pela extração inicial dos dados brutos de JSON e sua conversão para DataFrame.
*   **`src/etl_processor.py` (`ETLProcessor`)**: Encapsula as lógicas de limpeza, transformação e todos os filtros baseados nas regras de negócio (e.g., range `feed_measuredPerBird`, contagem de `loteComposto`, filtro inicial/final, filtro por R²).
*   **`src/curve_modeler.py` (`CurveModeler`)**: Contém a lógica para ajuste das curvas de consumo (`batchAge` vs `feed_measuredPerBird`) e cálculo do `confidence_level` (R²).
*   **`src/aggregator.py` (`Aggregator`)**: Realiza a agregação do consumo total de ração por ave para cada `loteComposto`.
*   **`src/plotter.py` (`Plotter`)**: Responsável pela geração e salvamento dos gráficos de consumo.

## 4. Tech Stack

*   **Linguagem**: Python 3.10+
*   **Ambiente Dev**: Pop_OS! / Windows 11 (com Docker)
*   **Bibliotecas Core**:
    *   `pandas` & `numpy`: Manipulação de dados.
    *   `scikit-learn`: Regressão Polinomial, Métricas (R²).
    *   `matplotlib` & `seaborn`: Visualização de dados.
    *   `pydantic`: Validação de modelos de dados (utilizado em `src/data_model.py` e `src/utils/data_loader.py`).
*   **Ambiente Virtual**: `.venv`

## 5. Como Executar

Para executar o pipeline completo:

1.  **Garanta o ambiente virtual**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2.  **Instale as dependências**:
    ```bash
    .venv/bin/python3 -m pip install -r requirements.txt
    ```
3.  **Execute o script principal**:
    ```bash
    .venv/bin/python3 main.py
    ```

O script irá processar os dados, gerar o arquivo CSV processado, o arquivo CSV agregado e salvar o plot da curva de consumo em `images/plots/curvas_consumo_new.png`.

## 6. Premissas e Regras de Negócio (Consolidadas)

Para a construção e refinamento do Gêmeo Digital, as seguintes premissas e regras foram consolidadas:

*   **Score de Manejo**: (Mortalidade 7d, Mortalidade Total, CA Ajustada, % Condenação) - *Conforme base de conhecimento.*
*   **Target Encoding**: Microrregião (80+ regiões resumidas pelo impacto no IEP) - *Conforme base de conhecimento.*
*   **Clustering (K-Means)**: Classificação dos aviários nos 4 quadrantes de eficiência (Alta Performance, Manejo de Ouro, Subutilizados, Críticos), com normalização (`StandardScaler`) obrigatória antes do K-Means e seleção de K=4 - *Conforme base de conhecimento.*
*   **Algoritmo Principal**: Random Forest Regressor para a taxa de esvaziamento diária (kg/dia) - *Conforme base de conhecimento.*
*   **Filtragem de `feed_measuredPerBird`**: Registros devem ter `feed_measuredPerBird` entre **15 e 250 (inclusive)**.
*   **Filtragem por Contagem Mínima de `loteComposto`**: Lotes compostos devem ter **no mínimo 15 registros** após o filtro de `feed_measuredPerBird`.
*   **Filtragem por Comportamento Inicial/Final de Consumo**: Lotes compostos são mantidos se o `feed_measuredPerBird` na **idade mínima do lote** estiver entre **0 e 50**, E na **idade máxima do lote** estiver entre **150 e 250**.
*   **Filtragem por Nível de Confiança ($R^2$)**: Lotes compostos são mantidos apenas se o seu `confidence_level` (R²) for **maior ou igual a 0.80**.
*   **Outliers (IEP)**: Valores de IEP abaixo de 200 ou acima de 500 devem ser sinalizados para conferência (possíveis erros de lançamento ou crises sanitárias) - *Conforme base de conhecimento.*

---