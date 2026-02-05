import pandas as pd
import os
import numpy as np

class ETLProcessor:
    def __init__(self, dataframe):
        self.df = dataframe

    def clean_and_transform_columns(self):
        """
        Cleans 'environmentName' and 'batchName' columns, converts them to integers,
        and creates the 'loteComposto' column.
        """
        if self.df is None or self.df.empty:
            print("No data in DataFrame for cleaning and transformation.")
            return self

        # Clean 'environmentName' and 'batchName'
        self.df['environmentName'] = self.df['environmentName'].astype(str).str.replace('AVIARIO ', '', regex=False)
        self.df['batchName'] = self.df['batchName'].astype(str).str.replace('Lote ', '', regex=False)
        
        # Convert to numeric, coercing errors to NaN and then to Int64 (to allow NaN)
        self.df['environmentName'] = pd.to_numeric(self.df['environmentName'], errors='coerce').astype('Int64')
        self.df['batchName'] = pd.to_numeric(self.df['batchName'], errors='coerce').astype('Int64')

        # Drop rows where conversion resulted in NaN
        self.df.dropna(subset=['environmentName', 'batchName'], inplace=True)

        print(f"DataFrame shape after cleaning environmentName and batchName: {self.df.shape}")

        # Create 'loteComposto' column and position it as the third column
        self.df['loteComposto'] = self.df['environmentName'].astype(str) + '-' + self.df['batchName'].astype(str)
        
        cols = self.df.columns.tolist()
        # Ensure 'loteComposto' is not already in cols if it was added in a prior run
        if 'loteComposto' in cols:
            cols.remove('loteComposto')
        
        # Insert 'loteComposto' at the third position (index 2), assuming first two cols are environmentName, batchName
        # If the order is not guaranteed, more robust insertion logic might be needed
        self.df = self.df[cols[:2] + ['loteComposto'] + cols[2:]]
        print(f"DataFrame shape after creating loteComposto: {self.df.shape}")
        return self

    def filter_data(self, feed_per_bird_min=15, feed_per_bird_max=250, lote_composto_min_count=15):
        """
        Filters data based on 'feed_measuredPerBird' range and 'loteComposto' group count.
        """
        if self.df is None or self.df.empty:
            print("No data in DataFrame for initial filtering.")
            return self

        # Drop rows where 'feed_measuredPerBird' is less than feed_per_bird_min or greater than feed_per_bird_max
        self.df['feed_measuredPerBird'] = pd.to_numeric(self.df['feed_measuredPerBird'], errors='coerce')
        self.df.dropna(subset=['feed_measuredPerBird'], inplace=True)
        
        self.df = self.df[(self.df['feed_measuredPerBird'] >= feed_per_bird_min) & 
                          (self.df['feed_measuredPerBird'] <= feed_per_bird_max)].copy()
        print(f"DataFrame shape after filtering feed_measuredPerBird (between {feed_per_bird_min} and {feed_per_bird_max}): {self.df.shape}")
        
        if not self.df.empty:
            print("loteComposto value counts after feed_measuredPerBird filter:")
            print(self.df['loteComposto'].value_counts().head(10))

            # Count unique 'loteComposto' values and drop groups with less than lote_composto_min_count rows
            lote_counts = self.df['loteComposto'].value_counts()
            to_keep = lote_counts[lote_counts >= lote_composto_min_count].index
            self.df = self.df[self.df['loteComposto'].isin(to_keep)]
            print(f"DataFrame shape after filtering loteComposto counts: {self.df.shape}")
        else:
            print("DataFrame is empty before filtering loteComposto counts.")
        return self

    def filter_by_start_end_consumption(self, initial_min=0, initial_max=50, final_min=150, final_max=250):
        """
        Filters loteComposto groups based on feed_measuredPerBird values at their
        minimum and maximum batchAge.
        """
        if self.df is None or self.df.empty:
            print("No data in DataFrame for start/end consumption filtering.")
            return self

        print(f"Applying start/end consumption filter (Initial: {initial_min}-{initial_max}, Final: {final_min}-{final_max})...")

        lotes_to_keep = []
        for lote_name, group in self.df.groupby('loteComposto'):
            # Find feed_measuredPerBird at min batchAge
            min_batch_age_row = group.loc[group['batchAge'].idxmin()]
            initial_consumption = min_batch_age_row['feed_measuredPerBird']

            # Find feed_measuredPerBird at max batchAge
            max_batch_age_row = group.loc[group['batchAge'].idxmax()]
            final_consumption = max_batch_age_row['feed_measuredPerBird']

            # Check conditions
            initial_ok = (initial_consumption >= initial_min) and (initial_consumption <= initial_max)
            final_ok = (final_consumption >= final_min) and (final_consumption <= final_max)

            if initial_ok and final_ok:
                lotes_to_keep.append(lote_name)
        
        initial_lotes_count = self.df['loteComposto'].nunique()
        self.df = self.df[self.df['loteComposto'].isin(lotes_to_keep)].copy()
        
        print(f"Number of loteComposto groups removed by start/end consumption filter: {initial_lotes_count - self.df['loteComposto'].nunique()}")
        print(f"DataFrame shape after start/end consumption filtering: {self.df.shape}")
        
        return self

    def filter_by_confidence_level(self, min_confidence=0.95):
        """
        Filters loteComposto groups based on their 'confidence_level' (R^2).
        Only groups with confidence_level >= min_confidence are retained.
        """
        if self.df is None or self.df.empty:
            print("No data in DataFrame for confidence level filtering.")
            return self
        if 'confidence_level' not in self.df.columns:
            print("Error: 'confidence_level' column not found for filtering. Ensure modeling has been performed.")
            return self

        print(f"Applying confidence level filter (R^2 >= {min_confidence})...")
        
        # Get unique loteComposto groups and their confidence levels
        lote_confidence = self.df[['loteComposto', 'confidence_level']].drop_duplicates()
        
        # Identify loteComposto groups to keep
        to_keep_lotes = lote_confidence[lote_confidence['confidence_level'] >= min_confidence]['loteComposto'].unique()

        # Filter the main DataFrame
        initial_lotes_count = self.df['loteComposto'].nunique()
        self.df = self.df[self.df['loteComposto'].isin(to_keep_lotes)].copy()

        print(f"Number of loteComposto groups removed by confidence level filter: {initial_lotes_count - self.df['loteComposto'].nunique()}")
        print(f"DataFrame shape after confidence level filtering: {self.df.shape}")
        
        return self

    def filter_by_aggregated_consumption_iqr(self, aggregated_df, consumption_column='total_consumption_per_lote_per_bird'):
        """
        Filters the main DataFrame to remove loteComposto groups that are outliers
        based on the IQR of their aggregated consumption per bird.
        """
        if self.df is None or self.df.empty:
            print("No data in main DataFrame for aggregated consumption IQR filtering.")
            return self
        if aggregated_df is None or aggregated_df.empty:
            print("No aggregated DataFrame provided for consumption IQR filtering.")
            return self
        if consumption_column not in aggregated_df.columns:
            print(f"Error: '{consumption_column}' column not found in aggregated DataFrame.")
            return self

        print("Applying aggregated consumption IQR outlier filter...")

        # Calculate Q1, Q3, and IQR for the aggregated consumption
        Q1 = aggregated_df[consumption_column].quantile(0.25)
        Q3 = aggregated_df[consumption_column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Identify outlier loteComposto groups from the aggregated data
        outlier_lotes = aggregated_df[
            (aggregated_df[consumption_column] < lower_bound) |
            (aggregated_df[consumption_column] > upper_bound)
        ]['loteComposto'].unique()

        # Filter the main DataFrame based on these outliers
        initial_lotes_count = self.df['loteComposto'].nunique()
        self.df = self.df[~self.df['loteComposto'].isin(outlier_lotes)].copy()
        
        print(f"Number of loteComposto groups removed by aggregated consumption IQR filter: {initial_lotes_count - self.df['loteComposto'].nunique()}")
        print(f"DataFrame shape after aggregated consumption IQR filtering: {self.df.shape}")

        return self


    def get_processed_dataframe(self):
        """Returns the processed DataFrame."""
        return self.df

    def save_data(self, output_filepath):
        """Saves the processed DataFrame to the output file."""
        if self.df is None or self.df.empty:
            print(f"No data to save after processing. Final DataFrame is empty.")
            return

        try:
            self.df.to_csv(output_filepath, sep=';', index=False)
            print(f"Processed data saved successfully to {output_filepath}")
        except Exception as e:
            print(f"Error saving processed data to CSV: {e}")