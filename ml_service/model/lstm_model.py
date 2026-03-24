import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class LSTMModelPredictor:
    \"\"\"
    LSTM Model for Stock Price Prediction (UP or DOWN).
    \"\"\"
    def __init__(self, inputShape=None, loadPath=None):
        if loadPath:
            self.loadModel(loadPath)
        elif inputShape:
            self.model = self._buildModel(inputShape)
        else:
            raise ValueError("Must provide either inputShape or loadPath")

    def _buildModel(self, inputShape):
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=inputShape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=25, activation='relu'))
        # Output layer for UP(1) or DOWN(0) prediction via sigmoid
        model.add(Dense(units=1, activation='sigmoid'))
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def train(self, xTrain, yTrain, epochs=10, batchSize=32):
        return self.model.fit(xTrain, yTrain, batch_size=batchSize, epochs=epochs, validation_split=0.1)

    def predict(self, xTest):
        return self.model.predict(xTest)

    def saveModel(self, path: str):
        self.model.save(path)

    def loadModel(self, path: str):
        self.model = tf.keras.models.load_model(path)
