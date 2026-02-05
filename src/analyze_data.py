from pathlib import Path
from src.utils.data_loader import load_silo_data

def analyze_single_silo_file(file_path: Path):
    """
    Loads a single silo data file and prints some key information.
    """
    print(f"Analyzing file: {file_path}")
    silo_data = load_silo_data(file_path)

    if silo_data:
        print(f"  Batch Name: {silo_data.batch.name}")
        print(f"  Environment Name: {silo_data.batch.environmentName}")
        print(f"  Batch Type: {silo_data.batch.batchType}")
        print(f"  Client Name: {silo_data.batch.clientName}")
        print(f"  Number of Batch Occurrences: {len(silo_data.batch.batchOccurrenceList)}")
        
        # Example of accessing ambience data
        print(f"  Geolocation City: {silo_data.ambience.geolocation.city}")
        
        # Find a specific measure in ambience results, e.g., 'windSpeed'
        for measure_result in silo_data.ambience.result:
            if measure_result.measure == "windSpeed" and measure_result.result:
                print(f"  Wind Speed (avgMeasured for first day): {measure_result.result[0].avgMeasured[0]}")
                break
    else:
        print(f"  Failed to load or parse data from {file_path}")

if __name__ == "__main__":
    # Assuming the first file in data/raw is what we want to analyze
    raw_data_dir = Path("data/raw")
    json_files = list(raw_data_dir.glob("*.json"))

    if json_files:
        analyze_single_silo_file(json_files[0])
    else:
        print(f"No JSON files found in {raw_data_dir}")
