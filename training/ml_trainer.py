"""
Machine Learning Trainer Module for Glute Fly AI Trainer
Trains TensorFlow model on collected pose data for automatic posture detection
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
from datetime import datetime

class MLTrainer:
    def __init__(self, data_dir="data", model_dir="models"):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.model = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
    def load_training_data(self, csv_files=None):
        """
        Load training data from CSV files
        If csv_files is None, load all CSV files from data directory
        """
        if csv_files is None:
            csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise ValueError("No CSV files found for training")
            
        print(f"📊 Loading data from {len(csv_files)} files...")
        
        all_data = []
        for csv_file in csv_files:
            file_path = os.path.join(self.data_dir, csv_file)
            try:
                df = pd.read_csv(file_path)
                all_data.append(df)
                print(f"  ✅ Loaded {len(df)} rows from {csv_file}")
            except Exception as e:
                print(f"  ❌ Error loading {csv_file}: {e}")
                
        if not all_data:
            raise ValueError("No valid data loaded")
            
        # Combine all data
        combined_data = pd.concat(all_data, ignore_index=True)
        print(f"📊 Total training data: {len(combined_data)} rows")
        
        return combined_data
        
    def prepare_features_and_labels(self, data):
        """
        Prepare features (landmarks) and labels for training
        """
        print("🔧 Preparing features and labels...")
        
        # Extract landmark features (x0, y0, z0, ..., x32, y32, z32)
        landmark_columns = []
        for i in range(33):
            landmark_columns.extend([f'x{i}', f'y{i}', f'z{i}'])
            
        # Check if all landmark columns exist
        missing_columns = [col for col in landmark_columns if col not in data.columns]
        if missing_columns:
            print(f"⚠️  Missing landmark columns: {missing_columns[:10]}...")
            # Use only available landmark columns
            available_landmark_columns = [col for col in landmark_columns if col in data.columns]
            X = data[available_landmark_columns].values
        else:
            X = data[landmark_columns].values
            
        print(f"📊 Feature shape: {X.shape}")
        
        # Prepare labels
        if 'label' in data.columns:
            y = data['label'].values
        else:
            raise ValueError("No 'label' column found in data")
            
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        print(f"📊 Label classes: {self.label_encoder.classes_}")
        print(f"📊 Label distribution: {np.bincount(y_encoded)}")
        
        return X, y_encoded
        
    def create_model(self, input_shape, num_classes):
        """
        Create TensorFlow model for posture classification
        """
        print("🏗️  Creating TensorFlow model...")
        
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(input_shape,)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("✅ Model created successfully")
        return model
        
    def train_model(self, X, y, test_size=0.2, epochs=50, batch_size=32):
        """
        Train the model on the provided data
        """
        print("🚀 Starting model training...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"📊 Training set: {X_train.shape[0]} samples")
        print(f"📊 Test set: {X_test.shape[0]} samples")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create model
        self.model = self.create_model(X_train.shape[1], len(np.unique(y)))
        
        # Train model
        history = self.model.fit(
            X_train_scaled, y_train,
            validation_data=(X_test_scaled, y_test),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_accuracy = self.model.evaluate(X_test_scaled, y_test, verbose=0)
        print(f"📊 Test Accuracy: {test_accuracy:.4f}")
        
        # Predictions for detailed evaluation
        y_pred = self.model.predict(X_test_scaled)
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred_classes, 
                                  target_names=self.label_encoder.classes_))
        
        return history
        
    def save_model(self, model_name=None):
        """
        Save trained model and preprocessing objects
        """
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
            
        if model_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"glute_fly_model_{timestamp}"
            
        model_path = os.path.join(self.model_dir, model_name)
        os.makedirs(model_path, exist_ok=True)
        
        # Save model
        self.model.save(os.path.join(model_path, "model.h5"))
        
        # Save preprocessing objects
        joblib.dump(self.label_encoder, os.path.join(model_path, "label_encoder.pkl"))
        joblib.dump(self.scaler, os.path.join(model_path, "scaler.pkl"))
        
        print(f"💾 Model saved to: {model_path}")
        return model_path
        
    def load_model(self, model_path):
        """
        Load trained model and preprocessing objects
        """
        print(f"📂 Loading model from: {model_path}")
        
        # Load model
        self.model = tf.keras.models.load_model(os.path.join(model_path, "model.h5"))
        
        # Load preprocessing objects
        self.label_encoder = joblib.load(os.path.join(model_path, "label_encoder.pkl"))
        self.scaler = joblib.load(os.path.join(model_path, "scaler.pkl"))
        
        print("✅ Model loaded successfully")
        
    def predict_posture(self, landmarks):
        """
        Predict posture from landmark data
        """
        if self.model is None:
            raise ValueError("No model loaded. Load or train model first.")
            
        # Prepare input data
        if isinstance(landmarks, dict):
            # Convert dict to array
            landmark_array = []
            for i in range(33):
                if i in landmarks:
                    landmark_array.extend([landmarks[i][0], landmarks[i][1], landmarks[i][2]])
                else:
                    landmark_array.extend([0.0, 0.0, 0.0])
            X = np.array([landmark_array])
        else:
            X = np.array([landmarks])
            
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)
        predicted_class = np.argmax(prediction, axis=1)[0]
        confidence = np.max(prediction, axis=1)[0]
        
        # Decode label
        predicted_label = self.label_encoder.inverse_transform([predicted_class])[0]
        
        return predicted_label, confidence
        
    def get_model_info(self):
        """
        Get information about the current model
        """
        if self.model is None:
            return "No model loaded"
            
        info = {
            'model_summary': self.model.summary(),
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape,
            'num_classes': len(self.label_encoder.classes_),
            'class_names': self.label_encoder.classes_.tolist()
        }
        
        return info

# Example usage:
if __name__ == "__main__":
    trainer = MLTrainer()
    
    try:
        # Load training data
        data = trainer.load_training_data()
        
        # Prepare features and labels
        X, y = trainer.prepare_features_and_labels(data)
        
        # Train model
        history = trainer.train_model(X, y, epochs=10)  # Reduced epochs for demo
        
        # Save model
        model_path = trainer.save_model("demo_model")
        
        print("🎉 Training completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        print("💡 Make sure you have collected some training data first!")
