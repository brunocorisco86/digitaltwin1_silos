import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.utils.data_loader import load_silo_data
from src.data_model import SiloData, Consumption, ConsumptionItem, FeedMetrics, FeedDeliveryMetrics # Import new models

def generate_consumption_dataset_v2():
    """
    Generates a CSV dataset with feed consumption data based on detailed specifications
    from the top-level 'consumption' object in the JSON files.
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
        if not silo_data or not silo_data.consumption or not silo_data.consumption.result:
            print(f"Aviso: Nenhum objeto 'consumption' válido ou 'consumption.result' encontrado no arquivo {file_path}. Pulando.")
            continue # Skip files without a valid consumption object or empty result list

        environment_name = silo_data.batch.environmentName
        batch_name = silo_data.batch.name
        client_name = silo_data.batch.clientName

        # Calculate preBatch_feedDelivery_measured from consumption.preBatchInfo
        preBatch_feedDelivery_total = 0.0
        if silo_data.consumption.preBatchInfo:
            for item in silo_data.consumption.preBatchInfo:
                if item.feedDelivery and item.feedDelivery.measured is not None:
                    preBatch_feedDelivery_total += item.feedDelivery.measured
                # If preBatch_feedDelivery_measured should come from manual in preBatchInfo
                # if item.feedDelivery and item.feedDelivery.manual is not None:
                #     preBatch_feedDelivery_total += item.feedDelivery.manual

        has_relevant_data_in_file = False

        # Iterate through consumption.result directly for main data extraction
        for consumption_item in silo_data.consumption.result:
            record: Dict[str, Any] = {
                "environmentName": environment_name,
                "batchName": batch_name,
                "clientName": client_name,
                "batchAge": consumption_item.batchAge,
                "preBatch_feedDelivery_measured": preBatch_feedDelivery_total,
                "feedDelivery_measured": consumption_item.feedDelivery.measured if consumption_item.feedDelivery and consumption_item.feedDelivery.measured is not None else 0.0,
                "feed_measured": consumption_item.feed.measured if consumption_item.feed and consumption_item.feed.measured is not None else 0.0,
                "feed_manual_measured": consumption_item.feed.manual if consumption_item.feed and consumption_item.feed.manual is not None else 0.0,
                "feed_measuredPerBird": consumption_item.feed.measuredPerBird if consumption_item.feed and consumption_item.feed.measuredPerBird is not None else 0.0,
                "siloEmptyTime": consumption_item.siloEmptyTime if consumption_item.siloEmptyTime is not None else 0,
                "siloNoConsumptionTime": consumption_item.siloNoConsumptionTime if consumption_item.siloNoConsumptionTime is not None else 0,
            }
            
            # If any of the main feed/feedDelivery values are present, consider it relevant
            if record["feedDelivery_measured"] > 0 or \
               record["feed_measured"] > 0 or \
               record["feed_manual_measured"] > 0 or \
               record["feed_measuredPerBird"] > 0 or \
               record["siloEmptyTime"] > 0 or \
               record["siloNoConsumptionTime"] > 0:
                has_relevant_data_in_file = True

            all_records.append(record)
        
        if not has_relevant_data_in_file and preBatch_feedDelivery_total == 0:
            print(f"Aviso: Nenhum dado de consumo de ração relevante encontrado no objeto 'consumption' do arquivo {file_path}. Pulando.")


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
        # Note: Pydantic models already ensure None for missing fields, then fillna makes them 0
        df = df.fillna(0)
        
        df.to_csv(output_csv_path, sep=';', index=False)
        print(f"Dataset de consumo de ração gerado com sucesso em: {output_csv_path}")
    else:
        print("Nenhum dado de consumo de ração processado para gerar o dataset.")

if __name__ == "__main__":
    generate_consumption_dataset_v2()
