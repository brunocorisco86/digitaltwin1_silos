# Gêmeo Digital de Silos: Inteligência de Dados no Campo

## O Gêmeo Digital como Elo entre o Campo e a Tecnologia
O projeto do Gêmeo Digital surge para eliminar a incerteza operacional no monitoramento de estoques de ração em aviários desprovidos de sensores físicos. Ao converter dados zootécnicos e estruturais em previsões precisas de esvaziamento, a solução atua como uma ponte estratégica entre as necessidades reais do campo e o desenvolvimento tecnológico. O foco primordial reside na otimização logística da C.Vale, visando a redução de custos de frete e a garantia inegociável do bem-estar animal através da segurança alimentar.

## Arquitetura de Dados: Do MTech ao Insight Operacional
A estrutura técnica do projeto baseia-se em uma ingestão automatizada de dados provenientes dos sistemas MTech (versão AMINO) e SAP, assegurando a integridade da informação desde a origem. O pipeline de dados é orquestrado via agentes de IA em ambientes Docker, garantindo escalabilidade e portabilidade para a solução.

| Etapa | Descrição | Ferramentas |
| :--- | :--- | :--- |
| **Ingestão** | Coleta de dados zootécnicos e estruturais | MTech, SAP |
| **Processamento** | ETL robusto e engenharia de atributos | Python, Pandas |
| **Inteligência** | Clustering de eficiência e Modelagem preditiva | Scikit-Learn |
| **Entrega** | Dashboards e alertas em tempo real | Power BI, Telegram |

## Qualidade de Dados e Premissas de ETL
Para garantir a confiabilidade do modelo, aplicamos filtros rigorosos de qualidade. O consumo medido por ave (`feed_measuredPerBird`) é limitado ao intervalo entre 15g e 250g, eliminando outliers causados por erros de lançamento. Além disso, apenas lotes com um histórico mínimo de 15 registros são considerados, assegurando que a inteligência do modelo seja construída sobre bases estatísticas sólidas e não sobre ruídos informacionais.

## Variabilidade do Consumo por Idade do Lote
A análise estatística através de boxplots revela a dispersão do consumo de ração ao longo dos 48 dias do ciclo. Observamos um aumento consistente na mediana do consumo, acompanhado por uma maior variabilidade nas fases finais (35-48 dias). Essa dispersão justifica a necessidade de um modelo de Machine Learning capaz de lidar com a incerteza e os desvios de padrão que métodos lineares simples não conseguiriam capturar.

## Clusterização de Eficiência: Quadrantes de Desempenho
A metodologia de clustering utiliza o algoritmo K-Means para segmentar os aviários em quatro perfis distintos, baseando-se na Pontuação Estrutural e no IEP (Índice de Eficiência Produtiva) Mediana. Esta classificação permite uma gestão visual e direcionada, identificando desde unidades de excelência até aquelas que necessitam de intervenção técnica imediata.

| Perfil | Características Principais | Ação Estratégica |
| :--- | :--- | :--- |
| **Manejo de Ouro** | Alta eficiência e estrutura otimizada | Referência de padrão |
| **Alta Performance** | Resultados sólidos com ajustes finos | Manutenção preventiva |
| **Subutilizados** | Gap de manejo em boa estrutura | Treinamento técnico |
| **Críticos** | Baixo desempenho e gargalos estruturais | Auditoria e intervenção |

## Comportamento do Consumo por Perfil de Eficiência
A análise das curvas medianas por cluster demonstra que o perfil **Manejo de Ouro** mantém consistentemente o maior consumo e eficiência ao longo de todo o ciclo. Em contrapartida, os aviários **Críticos** e **Subutilizados** apresentam curvas de consumo mais baixas e instáveis, especialmente após os 25 dias de vida. Essa diferenciação é crucial para o Gêmeo Digital ajustar a taxa de esvaziamento do silo conforme o perfil específico de cada produtor.

## Impacto da Infraestrutura no Consumo de Ração
A segmentação por **Grupo de Pontuação Máxima** (Estrutura) revela que aviários com pontuações mais baixas (0-20) apresentam paradoxalmente picos de consumo instáveis ou ineficientes em fases tardias, possivelmente devido a desperdícios ou falhas de ambiência. Aviários com pontuação elevada (81-100) exibem curvas mais previsíveis e controladas, reforçando que a qualidade da infraestrutura é um preditor direto da estabilidade logística.

## O Motor do Gêmeo: Modelagem Preditiva
O núcleo preditivo do Gêmeo Digital é impulsionado pelo algoritmo **Random Forest Regressor**, escolhido por sua capacidade superior em capturar as complexas não-linearidades do consumo animal. O modelo utiliza variáveis críticas como a idade do lote, a pontuação estrutural e o cluster de eficiência para gerar previsões diárias. A validação é realizada através de métricas de Erro Médio Absoluto (MAE), garantindo que as previsões sejam robustas e generalizáveis para diferentes cenários produtivos.

## Curvas de Consumo e Assinatura Digital
As curvas de consumo representam a "assinatura digital" de cada lote, permitindo a comparação entre o comportamento real e o predito. Através de técnicas de suavização por média móvel (Rolling Window de 3 dias), conseguimos eliminar oscilações diárias e ruídos de pesagem, entregando uma visão clara do padrão biológico de crescimento. A transparência sobre os níveis de confiança do modelo em cada fase do ciclo reforça a segurança na tomada de decisão logística.

## Próximos Passos e Integração Operacional
A evolução do projeto contempla a integração total com os dashboards de logística da C.Vale e a expansão para variáveis ambientais, como temperatura e umidade. O objetivo final é transformar o Gêmeo Digital em um assistente onipresente que não substitui o técnico de campo, mas o mune com uma "visão de raio-X" sobre os silos, garantindo que a logística nunca seja um gargalo para a produção de proteína animal.
