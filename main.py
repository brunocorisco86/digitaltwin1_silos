import os
from pathlib import Path
from src.data_extractor import DataExtractor
from src.etl_processor import ETLProcessor
from src.curve_modeler import CurveModeler
from src.plotter import Plotter
from src.aggregator import Aggregator # Import the Aggregator class

def main():
    script_dir = os.path.dirname(__file__)
    project_root = Path(script_dir)
    
    # Define paths relative to the project root
    raw_data_dir = project_root / "data" / "raw"
    processed_output_file = project_root / "data" / "processed" / "dataset_consumo_processed.csv"
    aggregated_output_file = project_root / "data" / "processed" / "aggregated_consumption_per_bird.csv" # New aggregated output file
    plot_output_filename = "curvas_consumo_new.png" 

    print("--- Starting Enhanced ETL Process ---")

    # 1. Extract Data from Raw JSON files
    print("\n--- Phase 1: Data Extraction ---")
    data_extractor = DataExtractor(raw_data_dir)
    data_extractor.extract_from_json()
    df_extracted = data_extractor.get_extracted_dataframe()

    if df_extracted is None or df_extracted.empty:
        print("Data extraction did not produce any data. Exiting.")
        return

    # 2. Initial ETL Processing (Cleaning and Filtering)
    print("\n--- Phase 2: Initial ETL Processing (Cleaning and Filtering) ---")
    etl_processor = ETLProcessor(df_extracted)
    etl_processor.clean_and_transform_columns() \
                 .filter_data() # Includes feed_measuredPerBird range and loteComposto count filter
    
    df_processed = etl_processor.get_processed_dataframe()

    if df_processed is None or df_processed.empty:
        print("ETL did not produce any data after initial filtering. Exiting.")
        return

    # 3. Apply Start/End Consumption Filter
    print("\n--- Phase 3: Applying Start/End Consumption Filter ---")
    etl_processor = ETLProcessor(df_processed) # Re-initialize with df_processed for chaining
    etl_processor.filter_by_start_end_consumption()
    
    df_filtered_start_end = etl_processor.get_processed_dataframe()

    if df_filtered_start_end is None or df_filtered_start_end.empty:
        print("ETL did not produce any data after start/end consumption filtering. Exiting.")
        return

    # 4. Curve Modeling and Confidence Level Calculation
    print("\n--- Phase 4: Curve Modeling and Confidence Level Calculation ---")
    curve_modeler = CurveModeler(df_filtered_start_end) # Pass data after start/end filter
    curve_modeler.add_confidence_level()
    
    df_with_confidence = curve_modeler.get_modeled_dataframe()

    if df_with_confidence is None or df_with_confidence.empty:
        print("ETL did not produce any data after modeling. Exiting.")
        return

    # 5. Apply R^2 Filtering
    print("\n--- Phase 5: Applying R^2 Confidence Level Filter (R^2 >= 0.80) ---") 
    etl_processor = ETLProcessor(df_with_confidence) # Re-initialize with df_with_confidence for chaining
    etl_processor.filter_by_confidence_level(min_confidence=0.80)
    
    df_final = etl_processor.get_processed_dataframe()

    if df_final is None or df_final.empty:
        print("ETL did not produce any data after R^2 filtering. Exiting.")
        return

    # 6. Aggregate Consumption Per Bird
    print("\n--- Phase 6: Aggregating Consumption Per Bird ---")
    aggregator = Aggregator(df_final)
    aggregator.aggregate_consumption_per_bird()
    df_aggregated = aggregator.get_aggregated_dataframe()

    # Save aggregated data
    if df_aggregated is not None and not df_aggregated.empty:
        try:
            df_aggregated.to_csv(aggregated_output_file, sep=';', index=False)
            print(f"Aggregated consumption data saved successfully to {aggregated_output_file}")
        except Exception as e:
            print(f"Error saving aggregated consumption data to CSV: {e}")
    else:
        print("No aggregated data to save.")

    # 7. Save final processed data (df_final is already set in etl_processor in previous step)
    print("\n--- Phase 7: Saving Final Processed Data ---")
    etl_processor.save_data(processed_output_file)

    # 8. Generate and save plot
    print("\n--- Phase 8: Generating Consumption Curves Plot ---")
    plotter = Plotter(df_final)
    plotter.plot_consumption_curves(output_filename=plot_output_filename)

    print("\n--- Enhanced ETL Process Completed Successfully ---")

if __name__ == "__main__":
    main()