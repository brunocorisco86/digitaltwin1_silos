import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from pathlib import Path

class Plotter:
    def __init__(self, dataframe):
        self.df = dataframe
        self.output_dir = Path("images/plots")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_consumption_curves(self, output_filename="curvas_consumo.png"):
        """
        Generates a plot of consumption curves ('feed_measuredPerBird' vs 'batchAge')
        for each 'loteComposto', color-coded by 'confidence_level'.
        Curves are smoothed using polynomial regression.
        """
        if self.df is None or self.df.empty:
            print("No data to plot consumption curves.")
            return

        print("\n--- Phase 5: Generating Consumption Curves Plot ---") # Fixed this print statement
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare legend handles and labels
        legend_handles = []
        legend_labels = []

        # Define colors for confidence levels
        color_map = {
            'red': {'label': 'Confidence < 0.90', 'threshold': 0.90},
            'green': {'label': '0.90 <= Confidence < 0.95', 'threshold': 0.95},
            'blue': {'label': '0.95 <= Confidence < 1.00', 'threshold': 1.00},
            'purple': {'label': 'Confidence = 1.00', 'threshold': 1.01} # Use 1.01 as a practical upper bound for confidence < 1
        }
        
        # Create dummy plots for legend
        # To avoid duplicate labels in the legend, we'll track which labels have been added
        added_labels = set()

        for color_name, info in color_map.items():
            label = info['label']
            if label not in added_labels:
                legend_handles.append(plt.Line2D([0], [0], color=color_name, lw=2, linestyle='-'))
                legend_labels.append(label)
                added_labels.add(label)


        unique_lotes = self.df['loteComposto'].unique()
        print(f"Plotting curves for {len(unique_lotes)} unique loteComposto groups...")

        for lote in unique_lotes:
            lote_df = self.df[self.df['loteComposto'] == lote].copy()
            
            # Get the confidence level for this lote
            confidence = lote_df['confidence_level'].iloc[0]

            # Determine color based on confidence level
            plot_color = 'gray' # Default color
            if confidence < color_map['red']['threshold']:
                plot_color = 'red'
            elif confidence < color_map['green']['threshold']:
                plot_color = 'green'
            elif confidence < color_map['blue']['threshold']:
                plot_color = 'blue'
            elif confidence >= color_map['blue']['threshold'] and confidence < color_map['purple']['threshold']: # For values >= 0.95 and < 1.00
                plot_color = 'blue'
            elif confidence >= color_map['purple']['threshold'] - 0.005: # For values approximately 1.00 (e.g., 0.9999999999999999)
                plot_color = 'purple'
            
            
            # Smoothing the curve using polynomial regression
            X = lote_df[['batchAge']].dropna()
            y = lote_df['feed_measuredPerBird'].dropna()

            if len(X) >= 2: # Need at least 2 points for a linear fit, 3 for quadratic
                # Use a quadratic model as used in CurveModeler, but can be adjusted if needed
                poly = PolynomialFeatures(degree=2)
                X_poly = poly.fit_transform(X)
                
                model = LinearRegression()
                model.fit(X_poly, y)
                
                # Predict over a sorted range for smooth curve
                x_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
                x_range_poly = poly.transform(x_range)
                y_pred = model.predict(x_range_poly)
                
                ax.plot(x_range, y_pred, color=plot_color, alpha=0.7)
            else:
                # If not enough data points for regression, plot points directly or skip
                ax.plot(X, y, 'o', color=plot_color, alpha=0.5, markersize=3) # Plot individual points if no smoothing possible


        ax.set_title("Consumption Curves by LoteComposto")
        ax.set_xlabel("Batch Age")
        ax.set_ylabel("Feed Measured Per Bird")
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Add legend
        # Ensure only unique labels are added to avoid redundant legend entries
        final_legend_handles = []
        final_legend_labels = []
        
        # Order the labels
        ordered_labels = ['Confidence < 0.90', '0.90 <= Confidence < 0.95', '0.95 <= Confidence < 1.00', 'Confidence = 1.00']
        
        for label in ordered_labels:
            if label in legend_labels:
                idx = legend_labels.index(label)
                final_legend_handles.append(legend_handles[idx])
                final_legend_labels.append(label)

        ax.legend(final_legend_handles, final_legend_labels, title="Confidence Level")

        output_path = self.output_dir / output_filename
        plt.tight_layout()
        plt.savefig(output_path)
        print(f"Plot saved successfully to {output_path}")
        plt.close(fig) # Close the plot to free memory