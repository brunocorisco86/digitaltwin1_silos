import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.utils.data_loader import load_silo_data
from src.data_model import SiloData, FeedDetail # Import FeedDetail

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
                # Assuming preBatch_feedDelivery_total comes from single value, not list
                # If it can be a list too, this needs to be updated. For now, stick to scalar value.
                if isinstance(occurrence.value, (int, float)):
                    preBatch_feedDelivery_total += float(occurrence.value)
                elif isinstance(occurrence.value, list): # Check for list of FeedDetail
                    for item in occurrence.value:
                        # Pydantic model will convert to FeedDetail, but direct dict access is safer here
                        if isinstance(item, dict) and 'measured' in item and isinstance(item['measured'], (int, float)):
                            preBatch_feedDelivery_total += float(item['measured'])


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
                    "feed_manual_measured": 0.0,
                    "feed_measuredPerBird": 0.0,
                    "siloEmptyTime": 0,
                    "siloNoConsumptionTime": 0
                }

            # Process feedDelivery
            if occurrence.type == 'feedDelivery':
                if isinstance(occurrence.value, (int, float)):
                    daily_data[batch_age]["feedDelivery_measured"] += float(occurrence.value)
                    has_relevant_data_in_file = True
                elif isinstance(occurrence.value, list): # Now handling list of FeedDetail
                    for item in occurrence.value:
                        # Try to parse as FeedDetail; if it fails, it might be a different dict structure
                        try:
                            feed_detail = FeedDetail(**item)
                            if feed_detail.measured is not None:
                                daily_data[batch_age]["feedDelivery_measured"] += feed_detail.measured
                            # Decide how to handle measuredPerBird and manual from feedDelivery here if needed
                            # For now, let's assume they are mainly for 'feed' type or are aggregated under measured
                        except Exception as e:
                            print(f"Aviso: Não foi possível parsear item de feedDelivery como FeedDetail no arquivo {file_path}: {item}. Erro: {e}")
                    has_relevant_data_in_file = True
            
            # Process feedConsumption (or 'feed' as user mentioned)
            elif occurrence.type == 'feedConsumption' or occurrence.type == 'feed': # Assuming 'feed' type exists
                if isinstance(occurrence.value, (int, float)):
                    daily_data[batch_age]["feed_measured"] += float(occurrence.value)
                    has_relevant_data_in_file = True
                elif isinstance(occurrence.value, list): # Now handling list of FeedDetail
                    for item in occurrence.value:
                        try:
                            feed_detail = FeedDetail(**item)
                            if feed_detail.measured is not None:
                                daily_data[batch_age]["feed_measured"] += feed_detail.measured
                            if feed_detail.manual is not None:
                                daily_data[batch_age]["feed_manual_measured"] += feed_detail.manual
                            if feed_detail.measuredPerBird is not None:
                                daily_data[batch_age]["feed_measuredPerBird"] += feed_detail.measuredPerBird # Aggregating per day, might need average or last value
                        except Exception as e:
                            print(f"Aviso: Não foi possível parsear item de feed/feedConsumption como FeedDetail no arquivo {file_path}: {item}. Erro: {e}")
                    has_relevant_data_in_file = True
            
            # SiloEmptyTime and SiloNoConsumptionTime are not explicitly found as occurrence types.
            # They would require specific occurrence types or complex derivation.

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
            "feedDelivery_measured", "feed_measured", "feed_manual_measured",
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