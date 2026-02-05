import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.utils.data_loader import load_silo_data
from src.data_model import SiloData

def generate_consumption_dataset_v2():
    """
    Generates a CSV dataset with feed consumption data based on detailed specifications.
    The output CSV will be saved as 'dataset_consumo.csv' in /data/processed.
    """
    raw_data_dir = Path("data/raw")
    processed_data_dir = Path("data/processed")
    output_csv_path = processed_data_dir / "dataset_consumo.csv"

    json_files = list(raw_data_dir.glob("*.json"))

    if not json_files:
        print(f"Nenhum arquivo JSON encontrado em {raw_data_dir}. Saindo.")
        return

    all_records: List[Dict[str, Any]] = []

    print(f"Processando {len(json_files)} arquivos JSON para o dataset de consumo...")

    for file_path in json_files:
        silo_data: Optional[SiloData] = load_silo_data(file_path)
        if not silo_data:
            continue # Skip files that failed to load or validate

        environment_name = silo_data.batch.environmentName
        batch_name = silo_data.batch.name
        client_name = silo_data.batch.clientName
        initial_date_ts = silo_data.batch.initialDate
        initial_date_dt = datetime.fromtimestamp(initial_date_ts)

        # Calculate preBatch_feedDelivery_measured for the entire batch
        preBatch_feedDelivery_total = 0.0
        for occurrence in silo_data.batch.batchOccurrenceList:
            if occurrence.type == 'feedDelivery' and occurrence.time < initial_date_ts:
                if isinstance(occurrence.value, (int, float)):
                    preBatch_feedDelivery_total += float(occurrence.value)
        
        # Aggregate daily consumption data
        daily_data: Dict[int, Dict[str, Any]] = {}
        has_relevant_data_in_file = False

        for occurrence in silo_data.batch.batchOccurrenceList:
            occurrence_dt = datetime.fromtimestamp(occurrence.time)
            batch_age = (occurrence_dt - initial_date_dt).days

            # Only consider occurrences within or after the batch started for daily aggregation
            if batch_age < 0:
                continue

            if batch_age not in daily_data:
                daily_data[batch_age] = {
                    "environmentName": environment_name,
                    "batchName": batch_name,
                    "clientName": client_name,
                    "batchAge": batch_age,
                    "preBatch_feedDelivery_measured": preBatch_feedDelivery_total, # This will be the same for all rows of the same batch
                    "feedDelivery_measured": 0.0,
                    "feed_measured": 0.0,
                    "feed_manual_measured": 0.0, # New field for manual feed
                    "feed_measuredPerBird": 0.0, # Not directly available, setting to 0
                    "siloEmptyTime": 0,          # Not directly available, setting to 0
                    "siloNoConsumptionTime": 0   # Not directly available, setting to 0
                }

            if occurrence.type == 'feedDelivery' and isinstance(occurrence.value, (int, float)):
                daily_data[batch_age]["feedDelivery_measured"] += float(occurrence.value)
                has_relevant_data_in_file = True
            elif occurrence.type == 'feedConsumption':
                if isinstance(occurrence.value, (int, float)):
                    daily_data[batch_age]["feed_measured"] += float(occurrence.value)
                    has_relevant_data_in_file = True
                elif isinstance(occurrence.value, dict) and 'manual' in occurrence.value and isinstance(occurrence.value['manual'], (int, float)):
                    daily_data[batch_age]["feed_manual_measured"] += float(occurrence.value['manual'])
                    has_relevant_data_in_file = True
            
            # Placeholder for feed_measuredPerBird, siloEmptyTime, siloNoConsumptionTime
            # If "feed.measuredPerBird" referred to a specific occurrence type or derivation logic, it would be handled here.

        if has_relevant_data_in_file or preBatch_feedDelivery_total > 0:
            for record in daily_data.values():
                all_records.append(record)
        else:
            print(f"Aviso: Nenhum dado de consumo de ração relevante encontrado no arquivo {file_path}. Pulando.")

    if all_records:
        df = pd.DataFrame(all_records)
        # Ensure consistent column order
        df = df[[
            "environmentName", "batchName", "clientName", "batchAge",
            "preBatch_feedDelivery_measured",
            "feedDelivery_measured", "feed_measured", "feed_manual_measured", # Added new field
            "feed_measuredPerBird",
            "siloEmptyTime", "siloNoConsumptionTime"
        ]]
        
        # Fill NaN values with 0 for statistical convenience as requested
        df = df.fillna(0)
        
        df.to_csv(output_csv_path, sep=';', index=False)
        print(f"Dataset de consumo de ração gerado com sucesso em: {output_csv_path}")
    else:
        print("Nenhum dado de consumo de ração processado para gerar o dataset.")

if __name__ == "__main__":
    generate_consumption_dataset_v2()