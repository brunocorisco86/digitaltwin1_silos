import pandas as pd
import numpy as np
import os
import sys

# Add the src directory to the system path to import analyze_silo_data
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.analyze_silo_data import analyze_silo_data

def generate_predictions(model, features, cluster_name_mapping, cluster_aviarios_file, output_file):
    # Load the cluster_aviarios_encoded.csv
    try:
        cluster_data = pd.read_csv(cluster_aviarios_file, sep=',')
    except FileNotFoundError:
        print(f"Error: The file '{cluster_aviarios_file}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading the cluster_aviarios_encoded.csv file: {e}")
        sys.exit(1)

    # Prepare the prediction dataset
    # Generate all combinations of Aviario and batchAge (1 to 70)
    unique_aviarios = cluster_data['Aviario'].unique()
    batch_ages = np.arange(1, 49) # From 1 to 48 days

    prediction_data = []
    for aviario in unique_aviarios:
        for batch_age in batch_ages:
            prediction_data.append({'Aviario': aviario, 'batchAge': batch_age})
    
    prediction_df = pd.DataFrame(prediction_data)

    # Merge with cluster_data to get other required features
    # Ensure correct columns are used for merging, and avoid merging 'PerfilDescritivo' or 'AreaAlojamento' if not needed as features directly
    features_to_merge = ['Aviario', 'PontuacaoMax', 'IEPMedian', 'ClassifCluster', 'PerfilDescritivo', 'AreaAlojamento', 'AreaAlojamento_Encoded']
    
    # Check if all features to merge exist in cluster_data
    if not all(f in cluster_data.columns for f in features_to_merge):
        missing = [f for f in features_to_merge if f not in cluster_data.columns]
        print(f"Error: Missing columns in cluster_aviarios_encoded.csv for merging: {missing}")
        sys.exit(1)

    prediction_df = pd.merge(prediction_df, cluster_data[features_to_merge], on='Aviario', how='left')

    # Ensure ClassifCluster is of the correct type (numerical) for the model, if it was treated as a number
    # If ClassifCluster is a feature, we need to ensure it's in the correct format.
    # Our `analyze_silo_data` function uses 'ClassifCluster' directly as numerical feature.

    # Filter out Aviarios that might not have all required features after merging
    # (e.g., if a new Aviario appeared in prediction_df that wasn't in cluster_data, though merge 'left' handles this by NaNs)
    initial_rows = len(prediction_df)
    prediction_df.dropna(subset=features, inplace=True)
    if len(prediction_df) < initial_rows:
        print(f"Warning: Dropped {initial_rows - len(prediction_df)} rows due to missing feature values after merging.")

    # Select and order features for prediction
    X_predict = prediction_df[features]

    # Make predictions
    predictions = model.predict(X_predict)
    prediction_df['predicted_feed_measuredPerBird'] = predictions.round(0)

    # Apply smoothing to predicted_feed_measuredPerBird per Aviario
    prediction_df['smoothed_feed_measuredPerBird'] = prediction_df.groupby('Aviario')['predicted_feed_measuredPerBird'].transform(lambda x: x.rolling(window=3, min_periods=1, center=True).mean().round(0))
    
    # Save results to CSV
    output_columns = [
        'Aviario', 'batchAge', 'predicted_feed_measuredPerBird', 'smoothed_feed_measuredPerBird',
        'PontuacaoMax', 'IEPMedian', 'ClassifCluster', 'PerfilDescritivo', 'AreaAlojamento'
    ]


    prediction_df[output_columns].to_csv(output_file, index=False)
    print(f"Predictions saved to '{output_file}'")

if __name__ == "__main__":
    current_dir = os.getcwd()
    
    # Define file paths
    main_dataset_file = os.path.join(current_dir, 'data', 'processed', 'dataset_consumo_processed.csv')
    cluster_aviarios_file = os.path.join(current_dir, 'data', 'processed', 'cluster_aviarios_encoded.csv')
    output_predictions_file = os.path.join(current_dir, 'data', 'processed', 'predicted_consumption_per_bird.csv')

    # Train the model (from analyze_silo_data.py)
    # We call the function and capture the returned model, features and mapping
    trained_model, model_features, cluster_map, cv_mae_mean, cv_mae_std = analyze_silo_data(main_dataset_file)
    
    # Print Cross-validation results captured from analyze_silo_data
    print(f"\nModel Cross-validation MAE: {cv_mae_mean:.2f} (+/- {cv_mae_std:.2f})")

    # Generate and save predictions
    generate_predictions(trained_model, model_features, cluster_map, cluster_aviarios_file, output_predictions_file)
