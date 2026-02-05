import pandas as pd

class Aggregator:
    def __init__(self, dataframe):
        self.df = dataframe
        self.aggregated_df = None

    def aggregate_consumption_per_bird(self):
        """
        Aggregates the total consumption per bird for each loteComposto across all batchAges.
        """
        if self.df is None or self.df.empty:
            print("No data in DataFrame for aggregation.")
            return self

        print("Aggregating Total Consumption Per Bird per LoteComposto...")
        
        # Group only by loteComposto and sum feed_measuredPerBird across all batchAges
        self.aggregated_df = self.df.groupby(['loteComposto'], as_index=False)['feed_measuredPerBird'].sum()
        self.aggregated_df.rename(columns={'feed_measuredPerBird': 'total_consumption_per_lote_per_bird'}, inplace=True)
        
        print(f"Aggregated DataFrame shape: {self.aggregated_df.shape}")
        print(f"Aggregated DataFrame head:\n{self.aggregated_df.head()}")
        
        return self

    def get_aggregated_dataframe(self):
        """Returns the aggregated DataFrame."""
        return self.aggregated_df
