
As seguintes premissas e transformações foram aplicadas durante o processo de ETL:

1.  **Localização dos Arquivos**:
    *   **Arquivo de Entrada**: O processo utilizou `data/processed/dataset_consumo.csv` como fonte de dados.
    *   **Arquivo de Saída**: O resultado processado foi salvo em `data/processed/dataset_consumo_processed.csv`.
    *   **Separador CSV**: Foi assumido que o arquivo CSV utiliza ponto e vírgula (`;`) como separador de colunas.

2.  **Limpeza e Transformação de Colunas**:
    *   **`environmentName`**: O prefixo 'AVIARIO ' foi removido e a coluna foi convertida para o tipo inteiro (`Int64`). Linhas onde a conversão resultou em valores inválidos foram descartadas.
    *   **`batchName`**: O prefixo 'Lote ' foi removido e a coluna foi convertida para o tipo inteiro (`Int64`). Linhas onde a conversão resultou em valores inválidos foram descartadas.

3.  **Criação e Posicionamento de Nova Coluna**:
    *   **`loteComposto`**: Uma nova coluna chamada `loteComposto` foi criada. Ela é a concatenação dos valores (já limpos) de `environmentName` e `batchName`, separados por um hífen (ex: "1126-33").
    *   Esta nova coluna foi inserida na terceira posição (índice 2) do DataFrame.

4.  **Filtragem de Dados (Premissas de Negócio)**:
    *   **Filtragem por `feed_measuredPerBird`**: A coluna `feed_measuredPerBird` foi convertida para numérico. Linhas com valores inválidos nesta coluna foram removidas. Foram mantidas apenas as linhas onde o valor de `feed_measuredPerBird` estava entre **15 e 250 (inclusive)**. Todas as outras linhas (menor que 15 ou maior que 250) foram descartadas.
    *   **Filtragem por Contagem de `loteComposto`**: Após a aplicação de todos os filtros anteriores, o processo verificou a contagem de ocorrências de cada valor único na coluna `loteComposto`. Grupos de `loteComposto` que possuíam **menos de 15 linhas** no total foram completamente removidos do conjunto de dados final. Apenas os grupos com 15 ou mais linhas foram retidos.

Espero que esta descrição detalhada ajude na sua auditoria.
