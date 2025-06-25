import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error, r2_score
from typing import List, Dict, Optional, Tuple
import io
import joblib

class MachineLearningService:
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
    
    def train_methylation_predictor(
        self,
        methylation_data: bytes,
        phenotype_data: bytes,
        phenotype_column: str,
        model_type: str = "classification"
    ) -> Dict:
        """Train ML model to predict phenotype from methylation data"""
        
        # Load data
        meth_df = pd.read_csv(io.BytesIO(methylation_data), sep='\t', index_col=0)
        pheno_df = pd.read_csv(io.BytesIO(phenotype_data), index_col=0)
        
        # Align samples
        common_samples = meth_df.columns.intersection(pheno_df.index)
        X = meth_df[common_samples].T  # Samples as rows
        y = pheno_df.loc[common_samples, phenotype_column]
        
        # Remove samples with missing phenotype
        valid_mask = ~y.isna()
        X = X[valid_mask]
        y = y[valid_mask]
        
        # Handle missing values in methylation data
        X = X.fillna(X.mean())
        
        # Feature selection (top variable features)
        feature_variance = X.var()
        top_features = feature_variance.nlargest(min(1000, len(feature_variance))).index
        X_selected = X[top_features]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_selected)
        
        # Train model
        if model_type == "classification":
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            results = self._train_classification_model(model, X_scaled, y, top_features.tolist())
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            results = self._train_regression_model(model, X_scaled, y, top_features.tolist())
        
        # Store model
        model_id = f"model_{len(self.models)}"
        self.models[model_id] = {
            "model": model,
            "scaler": self.scaler,
            "features": top_features.tolist(),
            "model_type": model_type
        }
        
        results["model_id"] = model_id
        return results
    
    def _train_classification_model(
        self, 
        model, 
        X: np.ndarray, 
        y: pd.Series, 
        features: List[str]
    ) -> Dict:
        """Train and evaluate classification model"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Train model
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # ROC AUC (if binary classification)
        try:
            if len(np.unique(y)) == 2:
                auc = roc_auc_score(y_test, y_pred_proba[:, 1])
            else:
                auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
        except:
            auc = None
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5)
        
        # Feature importance
        feature_importance = list(zip(features, model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "model_type": "classification",
            "accuracy": float(accuracy),
            "auc": float(auc) if auc is not None else None,
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "feature_count": len(features),
            "top_features": feature_importance[:20],
            "sample_count": len(X),
            "class_distribution": y.value_counts().to_dict()
        }
    
    def _train_regression_model(
        self, 
        model, 
        X: np.ndarray, 
        y: pd.Series, 
        features: List[str]
    ) -> Dict:
        """Train and evaluate regression model"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        # Train model
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        # Feature importance
        feature_importance = list(zip(features, model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "model_type": "regression",
            "mse": float(mse),
            "rmse": float(np.sqrt(mse)),
            "r2": float(r2),
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "feature_count": len(features),
            "top_features": feature_importance[:20],
            "sample_count": len(X),
            "target_stats": {
                "mean": float(y.mean()),
                "std": float(y.std()),
                "min": float(y.min()),
                "max": float(y.max())
            }
        }
    
    def predict_new_samples(
        self,
        model_id: str,
        methylation_data: bytes
    ) -> Dict:
        """Make predictions on new methylation data"""
        
        if model_id not in self.models:
            return {"error": "Model not found"}
        
        model_info = self.models[model_id]
        model = model_info["model"]
        scaler = model_info["scaler"]
        features = model_info["features"]
        
        # Load new data
        meth_df = pd.read_csv(io.BytesIO(methylation_data), sep='\t', index_col=0)
        
        # Select features and align
        X_new = meth_df.loc[features].T  # Samples as rows
        X_new = X_new.fillna(X_new.mean())
        
        # Scale
        X_new_scaled = scaler.transform(X_new)
        
        # Predict
        predictions = model.predict(X_new_scaled)
        
        if model_info["model_type"] == "classification":
            probabilities = model.predict_proba(X_new_scaled)
            return {
                "predictions": predictions.tolist(),
                "probabilities": probabilities.tolist(),
                "sample_ids": X_new.index.tolist()
            }
        else:
            return {
                "predictions": predictions.tolist(),
                "sample_ids": X_new.index.tolist()
            }
    
    def get_model_interpretation(self, model_id: str) -> Dict:
        """Get model interpretation and feature importance"""
        
        if model_id not in self.models:
            return {"error": "Model not found"}
        
        model_info = self.models[model_id]
        model = model_info["model"]
        features = model_info["features"]
        
        # Feature importance
        importance_scores = model.feature_importances_
        feature_importance = [
            {"feature": feat, "importance": float(score)}
            for feat, score in zip(features, importance_scores)
        ]
        feature_importance.sort(key=lambda x: x["importance"], reverse=True)
        
        # Model parameters
        model_params = model.get_params()
        
        return {
            "model_type": model_info["model_type"],
            "feature_importance": feature_importance[:50],
            "model_parameters": {k: str(v) for k, v in model_params.items()},
            "feature_count": len(features)
        }
    
    def save_model(self, model_id: str, filepath: str) -> bool:
        """Save trained model to file"""
        try:
            if model_id in self.models:
                joblib.dump(self.models[model_id], filepath)
                return True
            return False
        except:
            return False
    
    def load_model(self, filepath: str, model_id: str) -> bool:
        """Load trained model from file"""
        try:
            self.models[model_id] = joblib.load(filepath)
            return True
        except:
            return False