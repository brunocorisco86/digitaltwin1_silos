import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from src.utils.data_loader import load_silo_data
from src.data_model import SiloData, Ambience, BatchOccurrence # Import Ambience for type checking

def generate_consumption_dataset():
    """
    Generates a CSV dataset with feed consumption data aggregated by batchAge.
    """
    raw_data_dir = Path("data/raw")
    processed_data_dir = Path("data/processed")
    output_csv_path = processed_data_dir / "consumption_data.csv"

    json_files = list(raw_data_dir.glob("*.json"))

    if not json_files:
        print(f"Nenhum arquivo JSON encontrado em {raw_data_dir}. Saindo.")
        return

    all_consumption_data: List[Dict[str, Any]] = []

    print(f"Processando {len(json_files)} arquivos JSON para dados de consumo de ração...")

    for file_path in json_files:
        silo_data: Optional[SiloData] = load_silo_data(file_path)
        if not silo_data:
            continue # Skip files that failed to load or validate

        # Initialize consumption data for this batch
        batch_consumption_daily: Dict[int, Dict[str, Any]] = {}

        # Extract basic batch info
        environment_name = silo_data.batch.environmentName
        batch_name = silo_data.batch.name
        client_name = silo_data.batch.clientName
        initial_date = datetime.fromtimestamp(silo_data.batch.initialDate)

        has_consumption_data = False

        for occurrence in silo_data.batch.batchOccurrenceList:
            occurrence_date = datetime.fromtimestamp(occurrence.time)
            batch_age = (occurrence_date - initial_date).days

            if batch_age < 0: # Skip occurrences before batch start
                continue

            # Ensure the daily entry exists
            if batch_age not in batch_consumption_daily:
                batch_consumption_daily[batch_age] = {
                    "environmentName": environment_name,
                    "batchName": batch_name,
                    "clientName": client_name,
                    "batchAge": batch_age,
                    "feedDelivery_total": 0.0,
                    "feedConsumption_total": 0.0
                }

            # Aggregate feed consumption data
            if occurrence.type == 'feedDelivery' and isinstance(occurrence.value, (int, float)):
                batch_consumption_daily[batch_age]["feedDelivery_total"] += float(occurrence.value)
                has_consumption_data = True
            elif occurrence.type == 'feedConsumption' and isinstance(occurrence.value, (int, float)):
                batch_consumption_daily[batch_age]["feedConsumption_total"] += float(occurrence.value)
                has_consumption_data = True
            # Note: "feed" as a measure is more ambiguous. Assuming 'feedConsumption' covers it for now.
            # "siloEmptyTime" and "siloNoConsumptionTime" are not directly available as occurrence types.

        # Add processed daily data if consumption data was found for this batch
        if has_consumption_data:
            for daily_data in batch_consumption_daily.values():
                all_consumption_data.append(daily_data)
        else:
            print(f"Aviso: Nenhum dado de consumo de ração relevante encontrado no arquivo {file_path}. Pulando.")

    if all_consumption_data:
        df = pd.DataFrame(all_consumption_data)
        # Ensure consistent column order and fill NaNs if any
        df = df[[
            "environmentName", "batchName", "clientName", "batchAge",
            "feedDelivery_total", "feedConsumption_total"
        ]].fillna(0)
        df.to_csv(output_csv_path, index=False)
        print(f"Dataset de consumo de ração gerado com sucesso em: {output_csv_path}")
    else:
        print("Nenhum dado de consumo de ração processado para gerar o dataset.")

if __name__ == "__main__":
    generate_consumption_dataset()