"""
Training Script for Glute Fly AI Trainer
Demonstrates how to train ML model on collected data
"""

import os
import sys
from ml_trainer import MLTrainer

def main():
    print("🤖 Glute Fly AI Trainer - Model Training")
    print("=" * 50)
    
    # Initialize trainer
    trainer = MLTrainer()
    
    try:
        # Check if data exists
        data_files = [f for f in os.listdir("data") if f.endswith('.csv')]
        
        if not data_files:
            print("❌ No training data found!")
            print("💡 Please collect some data first by running the trainer in data collection mode.")
            print("   Press 'd' in the trainer to start data collection.")
            return
        
        print(f"📊 Found {len(data_files)} data files:")
        for file in data_files:
            print(f"  - {file}")
        
        # Load training data
        print("\n📊 Loading training data...")
        data = trainer.load_training_data()
        
        # Prepare features and labels
        print("\n🔧 Preparing features and labels...")
        X, y = trainer.prepare_features_and_labels(data)
        
        # Train model
        print("\n🚀 Training model...")
        print("   This may take a few minutes...")
        
        history = trainer.train_model(X, y, epochs=50)
        
        # Save model
        print("\n💾 Saving model...")
        model_path = trainer.save_model("glute_fly_model")
        
        print(f"\n🎉 Training completed successfully!")
        print(f"📁 Model saved to: {model_path}")
        print(f"\n💡 To use the trained model:")
        print(f"   1. Run: python glute_fly_trainer_enhanced.py")
        print(f"   2. Press 'm' to load model")
        print(f"   3. Enter path: {model_path}")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Make sure you have collected training data")
        print("   - Check that CSV files are in the 'data' directory")
        print("   - Ensure data has proper landmark columns")

if __name__ == "__main__":
    main()
