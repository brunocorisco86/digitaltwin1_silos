import pandas as pd
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import numpy as np
import sys
import os

def analyze_silo_data(file_path):
    """
    Analyzes silo data, trains a RandomForestRegressor model, and returns
    the trained model, the list of features used, and the cluster name mapping.
    """
    # Load the dataset
    try:
        df = pd.read_csv(file_path, sep=',')
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading the CSV file: {e}")
        sys.exit(1)

    # 1. Quality Filtering
    # Filter by confidence_level
    df_filtered = df[df['confidence_level'] >= 0.8].copy()

    # Remove outliers from IEPMedian (values outside 200-500)
    df_filtered = df_filtered[(df_filtered['IEPMedian'] >= 200) & (df_filtered['IEPMedian'] <= 500)].copy()

    # Define features (X) and target (Y)
    features = ['AreaAlojamento_Encoded', 'batchAge','ClassifCluster', 'PontuacaoMax','IEPMedian']
    target = 'feed_measuredPerBird'
    sample_weight_col = 'confidence_level'

    # Drop rows with NaN values in relevant columns before encoding
    df_filtered.dropna(subset=features + [target, sample_weight_col], inplace=True)

    # Define the mapping based on the problem description
    cluster_name_mapping = {
        0: "Críticos",
        1: "Subutilizados",
        2: "Manejo de Ouro",
        3: "Alta Performance"
    }

    # Since ClassifCluster is already numerical, use it directly as a feature
    # and map its values to descriptive names for output
    
    # Create a descriptive column for ClassifCluster for use in output and filtering
    df_filtered['ClassifCluster_Descriptive'] = df_filtered['ClassifCluster'].map(cluster_name_mapping)

    # Ensure ClassifCluster is treated as a numerical feature for the model
    # (it already is, so no encoding needed, but we keep it in features)
    # The `features` list still contains 'ClassifCluster' (the numerical one)
    # The 'ClassifCluster_Descriptive' will be used only for presenting results by name.

    X = df_filtered[features] # features list still has 'ClassifCluster' (numerical)
    y = df_filtered[target]
    sample_weights = df_filtered[sample_weight_col]

    print("Data loaded and filtered successfully.")
    print(f"Number of samples after filtering: {len(df_filtered)}")
    print(f"Features used: {features}")
    print(f"Target used: {target}")

    # 3. Training a Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y, sample_weight=sample_weights)
    print("""
Random Forest Regressor trained successfully.""")

    # Cross-validation
    print("\nPerforming Cross-validation (5-Fold) with manual loop...")
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_mae_scores = []

    for train_index, val_index in cv.split(X, y, groups=sample_weights): # groups is ignored by KFold but useful if using GroupKFold
        X_train, X_val = X.iloc[train_index], X.iloc[val_index]
        y_train, y_val = y.iloc[train_index], y.iloc[val_index]
        sample_weights_train, sample_weights_val = sample_weights.iloc[train_index], sample_weights.iloc[val_index]

        fold_model = RandomForestRegressor(n_estimators=100, random_state=42)
        fold_model.fit(X_train, y_train, sample_weight=sample_weights_train)
        y_pred_val = fold_model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred_val)
        cv_mae_scores.append(mae)
    
    cv_mae_mean = np.mean(cv_mae_scores)
    cv_mae_std = np.std(cv_mae_scores)

    print(f"Cross-validation MAE: {cv_mae_mean:.2f} (+/- {cv_mae_std:.2f})")


    # 3. Extraia o feature_importances_ para definir o peso real de cada variável na taxa de esvaziamento.
    feature_importance_df = pd.DataFrame({
        'Feature': X.columns,
        'Importance': model.feature_importances_
    }).sort_values(by='Importance', ascending=False)

    print("""
Ranking de Importância das Variáveis:""")
    print(feature_importance_df.to_markdown(index=False))

    # 4. Avaliação por Cluster
    # Get unique numerical cluster values present in the filtered data
    unique_numerical_clusters = df_filtered['ClassifCluster'].unique()
    mae_results = {}

    for numerical_val in unique_numerical_clusters:
        descriptive_cluster_name = cluster_name_mapping.get(numerical_val, f"Unknown Cluster {numerical_val}")
        
        # Filter cluster_df using the numerical cluster value
        cluster_df = df_filtered[df_filtered['ClassifCluster'] == numerical_val].copy()
        
        if not cluster_df.empty:
            X_cluster = cluster_df[features] # Use the numerical 'ClassifCluster' column here
            y_cluster = cluster_df[target]
            
            y_pred_cluster = model.predict(X_cluster)
            mae_cluster = mean_absolute_error(y_cluster, y_pred_cluster)
            mae_results[descriptive_cluster_name] = mae_cluster
        else:
            mae_results[descriptive_cluster_name] = np.nan # No data for this cluster

    print("""
Métrica de Erro (MAE) para cada Cluster:""")
    mae_df = pd.DataFrame(mae_results.items(), columns=['Cluster', 'MAE']).sort_values(by='MAE')
    print(mae_df.to_markdown(index=False))

    return model, features, cluster_name_mapping, cv_mae_mean, cv_mae_std
