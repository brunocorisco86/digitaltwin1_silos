import pandas as pd
import os
from pathlib import Path
from src.utils.data_loader import load_silo_data
from src.data_model import SiloData, ConsumptionItem, FeedMetrics # Import necessary models

class DataExtractor:
    def __init__(self, raw_data_dir):
        self.raw_data_dir = Path(raw_data_dir)
        self.extracted_df = None

    def extract_from_json(self):
        """
        Extracts relevant data from raw JSON files in the specified directory
        and consolidates it into a pandas DataFrame.
        """
        all_records = []
        
        if not self.raw_data_dir.is_dir():
            print(f"Error: Raw data directory not found at {self.raw_data_dir}")
            return None

        json_files = list(self.raw_data_dir.glob("*.json"))
        print(f"Found {len(json_files)} JSON files in {self.raw_data_dir}")

        for json_file in json_files:
            silo_data = load_silo_data(json_file)
            if silo_data and silo_data.consumption:
                # Ensure consumption is a Consumption object, not a string or None
                if isinstance(silo_data.consumption, SiloData.model_fields['consumption'].annotation.__args__[0]): # This is a bit verbose to get Consumption type
                    consumption_data = silo_data.consumption
                    # Iterate through result items (main consumption data points)
                    for item in consumption_data.result:
                        record = {
                            'environmentName': consumption_data.environmentName,
                            'batchName': consumption_data.batchName,
                            'clientName': consumption_data.clientName,
                            'batchAge': item.batchAge,
                            'preBatch_feedDelivery_measured': item.feedDelivery.measured if item.feedDelivery and item.feedDelivery.measured is not None else 0.0,
                            'feedDelivery_measured': item.feedDelivery.measured if item.feedDelivery and item.feedDelivery.measured is not None else 0.0, # Assuming this is the same as preBatch_feedDelivery_measured if only one value is present
                            'feed_measured': item.feed.measured if item.feed and item.feed.measured is not None else 0.0,
                            'feed_manual_measured': item.feed.manual if item.feed and item.feed.manual is not None else 0.0,
                            'feed_measuredPerBird': item.feed.measuredPerBird if item.feed and item.feed.measuredPerBird is not None else 0.0,
                            'siloEmptyTime': item.siloEmptyTime if item.siloEmptyTime is not None else 0,
                            'siloNoConsumptionTime': item.siloNoConsumptionTime if item.siloNoConsumptionTime is not None else 0,
                            # Add other fields if necessary, ensuring to handle Optional types
                        }
                        all_records.append(record)
                    
                    # Also consider preBatchInfo if it contains relevant data
                    if consumption_data.preBatchInfo:
                        for item in consumption_data.preBatchInfo:
                            record = {
                                'environmentName': consumption_data.environmentName,
                                'batchName': consumption_data.batchName,
                                'clientName': consumption_data.clientName,
                                'batchAge': item.batchAge,
                                'preBatch_feedDelivery_measured': item.feedDelivery.measured if item.feedDelivery and item.feedDelivery.measured is not None else 0.0,
                                'feedDelivery_measured': item.feedDelivery.measured if item.feedDelivery and item.feedDelivery.measured is not None else 0.0,
                                'feed_measured': item.feed.measured if item.feed and item.feed.measured is not None else 0.0,
                                'feed_manual_measured': item.feed.manual if item.feed and item.feed.manual is not None else 0.0,
                                'feed_measuredPerBird': item.feed.measuredPerBird if item.feed and item.feed.measuredPerBird is not None else 0.0,
                                'siloEmptyTime': item.siloEmptyTime if item.siloEmptyTime is not None else 0,
                                'siloNoConsumptionTime': item.siloNoConsumptionTime if item.siloNoConsumptionTime is not None else 0,
                            }
                            all_records.append(record)

        if all_records:
            self.extracted_df = pd.DataFrame(all_records)
            # Reorder columns to match the original dataset_consumo.csv if possible for consistency
            # This is an example, adjust if your raw JSON structure implies a different order
            expected_columns = [
                'environmentName', 'batchName', 'clientName', 'batchAge',
                'preBatch_feedDelivery_measured', 'feedDelivery_measured', 'feed_measured',
                'feed_manual_measured', 'feed_measuredPerBird', 'siloEmptyTime', 'siloNoConsumptionTime'
            ]
            # Ensure all expected columns are present, fill missing with NaN if necessary
            for col in expected_columns:
                if col not in self.extracted_df.columns:
                    self.extracted_df[col] = np.nan
            self.extracted_df = self.extracted_df[expected_columns]

            print(f"Extracted DataFrame shape: {self.extracted_df.shape}")
            print(f"Extracted DataFrame columns: {self.extracted_df.columns.tolist()}")
        else:
            print("No records extracted from JSON files.")
            self.extracted_df = pd.DataFrame() # Return empty DataFrame to avoid None issues
        return self

    def get_extracted_dataframe(self):
        """Returns the extracted DataFrame."""
        return self.extracted_df
