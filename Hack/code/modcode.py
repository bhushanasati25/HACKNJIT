from flask import Flask, request, jsonify
from flask import render_template
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import joblib
import tensorflow as tf
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask

app = Flask(__name__)

# Paths for data and model storage
DATA_PATH = '/Users/ihack-pc/Downloads/Hack NJIT/Hack/healthcare-dataset-stroke-data.csv'
MODEL_PATH = 'model.keras'
SCALER_PATH = 'scaler.pkl'
COLUMNS_PATH = 'columns.pkl'  # Save the list of columns


# Define your route for the home page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/train_model')
def train_model_page():
    return render_template('train_model.html')

@app.route('/predict_risk')
def predict_risk_page():
    return render_template('predict_risk.html')



# Load data and preprocess
def load_data():
    health_data = pd.read_csv(DATA_PATH)
    imputer = SimpleImputer(strategy='median')
    health_data['bmi'] = imputer.fit_transform(health_data[['bmi']])

    # Check if 'smoking' column exists; if not, add it with a default value
    if 'smoking' not in health_data.columns:
        health_data['smoking'] = 'Nonsmoker'  # Default value for testing

    # Map the smoking values if present
    health_data['smoking'] = health_data['smoking'].map({
        'Nonsmoker': 'Nonsmoker',
        'Occasional Smoker': 'occasional_smoker',
        'Heavy Smoker': 'heavy_smoker'
    })

    # Encode categorical variables, including 'smoking'
    health_data = pd.get_dummies(health_data, columns=health_data.select_dtypes(include=['object']).columns, drop_first=True)
    health_data.drop('id', axis=1, inplace=True)

    # Save the list of columns
    joblib.dump(health_data.columns, COLUMNS_PATH)

    X = health_data.drop('stroke', axis=1)
    y = health_data['stroke']
    return X, y


# Train model and save scaler, model, and columns
@app.route('/train', methods=['POST'])
def train_model():
    X, y = load_data()
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    joblib.dump(scaler, SCALER_PATH)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = Sequential([
        Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        Dense(64, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=1)
    
    model.save(MODEL_PATH)
    return jsonify({"message": "Model trained and saved successfully!"})

# Scoring-based classification, including 'smoking'
def calculate_risk_score(sample):
    risk_score = 0

    # BMI scoring
    if sample['bmi'] < 20:
        risk_score += 1
    elif 20 <= sample['bmi'] <= 30:
        risk_score += 2
    else:
        risk_score += 3

    # Glucose level scoring
    if 70 <= sample['avg_glucose_level'] <= 130:
        risk_score += 1
    elif 130 < sample['avg_glucose_level'] <= 200:
        risk_score += 2
    else:
        risk_score += 3

    # Age scoring
    if sample['age'] < 20:
        risk_score += 1
    elif 20 <= sample['age'] < 40:
        risk_score += 2
    elif 40 <= sample['age'] < 60:
        risk_score += 3
    else:
        risk_score += 4

    # Hypertension and heart disease scoring
    if sample['hypertension'] == 1:
        risk_score += 2
    if sample['heart_disease'] == 1:
        risk_score += 2

    # Smoking scoring
    if 'smoking_occasional_smoker' in sample and sample['smoking_occasional_smoker'] == 1:
        risk_score += 1
    elif 'smoking_heavy_smoker' in sample and sample['smoking_heavy_smoker'] == 1:
        risk_score += 2

    return risk_score

def classify_risk(sample):
    risk_score = calculate_risk_score(sample)
    if risk_score <= 5:
        return "Low Risk", "Explanation: Low risk score based on health parameters."
    elif 6 <= risk_score <= 9:
        return "Medium Risk", "Explanation: Medium risk score based on health parameters."
    else:
        return "High Risk", "Explanation: High risk score due to multiple high-risk parameters."

# Predict endpoint for risk classification
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    required_fields = {'age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi', 'smoking'}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    sample = pd.DataFrame([data])

    # Load scaler, model, and columns used during training
    scaler = joblib.load(SCALER_PATH)
    model = tf.keras.models.load_model(MODEL_PATH)
    columns = joblib.load(COLUMNS_PATH)

    # Encode 'smoking' into dummy variables
    sample['smoking'] = sample['smoking'].map({
        'Nonsmoker': 'Nonsmoker',
        'Occasional Smoker': 'occasional_smoker',
        'Heavy Smoker': 'heavy_smoker'
    })
    sample = pd.get_dummies(sample)
    sample = sample.reindex(columns=columns, fill_value=0)

    # Drop the target column 'stroke' if it appears in the sample
    if 'stroke' in sample.columns:
        sample = sample.drop(columns=['stroke'])

    # Scale the sample
    sample_scaled = scaler.transform(sample)
    
    # Predict and classify
    prediction = model.predict(sample_scaled)
    risk_level, explanation = classify_risk(data)

    return jsonify({"Risk Level": risk_level, "Explanation": explanation})

if __name__ == '__main__':
    app.run(debug=True)




