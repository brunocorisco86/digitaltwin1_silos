import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score

class CurveModeler:
    def __init__(self, df):
        self.df = df
        self.confidence_column_name = 'confidence_level'

    def _fit_curve_and_calculate_confidence(self, group):
        """
        Fits a polynomial regression curve to the feed_measuredPerBird vs batchAge
        for a given loteComposto group and calculates an R-squared confidence level.
        """
        if len(group) < 3: # Need at least 3 points for a quadratic fit
            return pd.Series({self.confidence_column_name: np.nan})

        X = group[['batchAge']]
        y = group['feed_measuredPerBird']

        # Using PolynomialFeatures to create polynomial terms for batchAge
        poly = PolynomialFeatures(degree=2) # Starting with a quadratic curve
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)
        
        y_pred = model.predict(X_poly)
        confidence = r2_score(y, y_pred)
        
        return pd.Series({self.confidence_column_name: confidence})

    def add_confidence_level(self):
        """
        Calculates the confidence level for each loteComposto group based on curve fitting
        and adds it as a new column to the DataFrame.
        """
        if self.df is None or self.df.empty:
            print("No data to model consumption curve and calculate confidence level.")
            return self

        print("Modeling consumption curve and calculating confidence level...")
        confidence_df = self.df.groupby('loteComposto').apply(self._fit_curve_and_calculate_confidence).reset_index()
        self.df = pd.merge(self.df, confidence_df, on='loteComposto', how='left')
        
        print(f"DataFrame shape after adding {self.confidence_column_name}: {self.df.shape}")
        print("Confidence levels (first 5):")
        print(self.df[['loteComposto', self.confidence_column_name]].drop_duplicates().head())
        
        return self

    def get_modeled_dataframe(self):
        """Returns the DataFrame with confidence levels."""
        return self.df