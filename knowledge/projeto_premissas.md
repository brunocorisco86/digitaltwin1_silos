# Knowledge Base: Projeto Gêmeo Digital AgroCenter (C.Vale)

## 1. Escopo e Visão Geral

Desenvolvimento de um **Gêmeo Digital** para estimativa da taxa de esvaziamento de silos em aviários sem sensores. O projeto utiliza Machine Learning para converter dados zootécnicos e estruturais em previsões de estoque, visando otimização logística e bem-estar animal.

## 2. Pipeline de Dados (O Fluxo)

1. **Ingestão:** Extração de dados do MTech (versão AMINO) e SAP via conectores corporativos.
2. **Processamento & Feature Engineering:**
* Criação do **Score de Manejo** (Mortalidade 7d, Mortalidade Total, CA Ajustada, % Condenação).
* **Target Encoding** da Microrregião (80+ regiões resumidas pelo impacto no IEP).
* **Clustering (K-Means):** Classificação dos aviários nos 4 quadrantes de eficiência (Alta Performance, Manejo de Ouro, Subutilizados, Críticos).


3. **Modelagem (Engine do Gêmeo):**
* **Algoritmo Principal:** Random Forest Regressor.
* **Target:** Taxa de esvaziamento diária (kg/dia).


4. **Entrega:** Dashboards no Power BI e alertas via Telegram/AgroCenter.

## 3. Tech Stack (Ferramentas)

* **Linguagem:** Python 3.10+
* **Ambiente Dev:** Pop_OS! (Casa) / Windows 11 (Corporativo) com Docker.
* **IDE/Data Tools:** DBeaver (SQLite), VS Code, Jupyter Notebooks.
* **Bibliotecas Core:**
* `pandas` & `numpy`: Manipulação de dados.
* `scikit-learn`: K-Means, Random Forest, Scaling.
* `category_encoders`: Para o Target Encoding das microrregiões.
* `matplotlib` & `seaborn`: Visualização técnica (Cotovelo/Silhueta).


* **Orquestração de Agentes:** Agno (antigo Phidata) ou LangChain, rodando em containers Docker.

## 4. Estrutura do Repositório (Sugestão)

```text
/cvale-gemeo-digital
│
├── /data                # Datasets (dataset_iep_pontuacao.csv)
├── /notebooks           # Prototipagem (K-Means, Elbow Method)
├── /src                 # Scripts de produção
│   ├── clustering.py    # Lógica do K-Means e Quadrantes
│   ├── training.py      # Treinamento do Random Forest
│   └── encoding.py      # Target Encoding de Microrregiões
├── /docs                # Documentação do projeto e regras de negócio
├── docker-compose.yml   # Configuração do ambiente do Agente de IA
└── requirements.txt     # Dependências (scikit-learn, category_encoders, etc.)

```

## 5. Regras de Negócio para o Agente de IA

Para que o agente execute as demandas corretamente, ele deve seguir estas premissas:

* **Normalização OBRIGATÓRIA:** Antes de qualquer K-Means, os dados de IEP e Pontuação devem ser normalizados (`StandardScaler`).
* **Seleção de Clusters (K=4):** Baseado nas métricas de Silhueta e Cotovelo, o projeto está travado em 4 grupos para alinhar com a estratégia da diretoria.
* **Cuidado com Outliers:** Valores de IEP abaixo de 200 ou acima de 500 devem ser sinalizados para conferência (possíveis erros de lançamento ou crises sanitárias).

---
