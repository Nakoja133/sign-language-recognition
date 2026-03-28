import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

def load_data():
    """Load preprocessed data"""
    print("Loading preprocessed data...")
    with open("preprocessed_data.pkl", "rb") as f:
        data = pickle.load(f)
    
    X_train = data["X_train"]
    X_test  = data["X_test"]
    y_train = data["y_train"]
    y_test  = data["y_test"]
    classes = data["classes"]
    
    print(f"Training samples : {len(X_train)}")
    print(f"Testing samples  : {len(X_test)}")
    print(f"Number of classes: {len(classes)}")
    print(f"Classes          : {classes}\n")
    
    return X_train, X_test, y_train, y_test, classes

def build_model(input_shape, num_classes):
    """Build the neural network model"""
    model = Sequential([
        Dense(256, activation='relu', input_shape=(input_shape,)),
        BatchNormalization(),
        Dropout(0.3),

        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),

        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),

        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def plot_training(history):
    """Plot training results"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Accuracy plot
    ax1.plot(history.history['accuracy'], label='Train Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    
    # Loss plot
    ax2.plot(history.history['loss'], label='Train Loss')
    ax2.plot(history.history['val_loss'], label='Val Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('training_results.png')
    print("Training graph saved as training_results.png ✅")

def train():
    # Load data
    X_train, X_test, y_train, y_test, classes = load_data()
    num_classes = len(classes)
    
    # One-hot encode labels
    y_train_cat = to_categorical(y_train, num_classes)
    y_test_cat  = to_categorical(y_test,  num_classes)
    
    # Build model
    print("Building model...")
    model = build_model(X_train.shape[1], num_classes)
    model.summary()
    
    # Callbacks
    early_stop = EarlyStopping(
        monitor='val_accuracy',
        patience=10,
        restore_best_weights=True
    )
    checkpoint = ModelCheckpoint(
        'asl_model.keras',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
    
    # Train
    print("\nTraining started...")
    history = model.fit(
        X_train, y_train_cat,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test_cat),
        callbacks=[early_stop, checkpoint],
        verbose=1
    )
    
    # Evaluate
    print("\nEvaluating model...")
    loss, accuracy = model.evaluate(X_test, y_test_cat, verbose=0)
    print(f"Test Accuracy: {accuracy * 100:.2f}%")
    print(f"Test Loss    : {loss:.4f}")
    
    # Save classes
    with open("classes.pkl", "wb") as f:
        pickle.dump(classes, f)
    print("Classes saved to classes.pkl ✅")
    
    # Plot results
    plot_training(history)
    
    print("\nTraining complete! ✅")
    print("Model saved as asl_model.keras ✅")

if __name__ == "__main__":
    train()