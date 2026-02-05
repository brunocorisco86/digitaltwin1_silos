from pathlib import Path
from typing import Set, Dict, Optional
import json

from src.utils.data_loader import load_silo_data
from src.data_model import SiloData

def extract_unique_values():
    """
    Extracts unique values for key fields from all silo data JSON files
    and prints them in Markdown format (pt-br).
    """
    raw_data_dir = Path("data/raw")
    json_files = list(raw_data_dir.glob("*.json"))

    if not json_files:
        print(f"Nenhum arquivo JSON encontrado em {raw_data_dir}. Saindo.")
        return

    unique_batch_types: Set[str] = set()
    unique_batch_statuses: Set[str] = set()
    unique_client_names: Set[str] = set()
    unique_environment_names: Set[str] = set()
    unique_occurrence_types: Set[str] = set()
    unique_ambience_measures: Set[str] = set()
    unique_cities: Set[str] = set()
    unique_states: Set[str] = set()
    unique_countries: Set[str] = set()
    unique_reference_measures: Set[str] = set()
    unique_reference_types: Set[str] = set()
    unique_reference_categories: Set[str] = set()
    unique_reference_modes: Set[str] = set()

    print(f"Processando {len(json_files)} arquivos JSON...")

    for file_path in json_files:
        silo_data: Optional[SiloData] = load_silo_data(file_path)
        if silo_data:
            # Batch data
            unique_batch_types.add(silo_data.batch.batchType)
            unique_batch_statuses.add(silo_data.batch.batchStatus)
            unique_client_names.add(silo_data.batch.clientName)
            unique_environment_names.add(silo_data.batch.environmentName)

            for occurrence in silo_data.batch.batchOccurrenceList:
                unique_occurrence_types.add(occurrence.type)

            if silo_data.batch.batchReferences and 'referenceList' in silo_data.batch.batchReferences:
                for ref in silo_data.batch.batchReferences['referenceList']:
                    unique_reference_measures.add(ref['measure'])
                    unique_reference_types.add(ref['referenceType'])
                    unique_reference_categories.add(ref['referenceCategory'])
                    unique_reference_modes.add(ref['referenceMode'])

            # Ambience data - check if ambience is not None
            if silo_data.ambience:
                unique_cities.add(silo_data.ambience.geolocation.city)
                unique_states.add(silo_data.ambience.geolocation.state)
                unique_countries.add(silo_data.ambience.geolocation.country)

                for measure_result in silo_data.ambience.result:
                    unique_ambience_measures.add(measure_result.measure)
        else:
            # The data_loader already prints an error message, so no need to repeat here
            pass

    # Print results in Markdown format (pt-br)
    print("\n# Valores Únicos Extraídos dos Dados do Silo\n")

    print("## Informações do Lote")
    print(f"- **Tipos de Lote:** {', '.join(sorted(list(unique_batch_types)))}")
    print(f"- **Status do Lote:** {', '.join(sorted(list(unique_batch_statuses)))}")
    print(f"- **Nomes dos Clientes:** {', '.join(sorted(list(unique_client_names)))}")
    print(f"- **Nomes dos Ambientes:** {', '.join(sorted(list(unique_environment_names)))}")
    print(f"- **Tipos de Ocorrência do Lote:** {', '.join(sorted(list(unique_occurrence_types)))}")
    
    print("\n## Referências do Lote")
    print(f"- **Medidas de Referência:** {', '.join(sorted(list(unique_reference_measures)))}")
    print(f"- **Tipos de Referência:** {', '.join(sorted(list(unique_reference_types)))}")
    print(f"- **Categorias de Referência:** {', '.join(sorted(list(unique_reference_categories)))}")
    print(f"- **Modos de Referência:** {', '.join(sorted(list(unique_reference_modes)))}")

    print("\n## Informações de Ambiente")
    print(f"- **Cidades:** {', '.join(sorted(list(unique_cities)))}")
    print(f"- **Estados:** {', '.join(sorted(list(unique_states)))}")
    print(f"- **Países:** {', '.join(sorted(list(unique_countries)))}")
    print(f"- **Medidas de Ambiente:** {', '.join(sorted(list(unique_ambience_measures)))}")


if __name__ == "__main__":
    extract_unique_values()
