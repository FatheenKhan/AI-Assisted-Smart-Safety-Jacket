import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load your heart rate dataset (assuming it's in a CSV file)
heart_data = pd.read_csv("running_pulse_data.csv")

# Display some sample values from the "pulse" column for debugging
print("Sample values from the 'pulse' column:")
print(heart_data.head())

# Create the "abnormal" column based on pulse values
heart_data["condition"] = heart_data[" Pulse"].apply(lambda x: 1 if x < 60 or x > 100 else 0)

# Display some sample values from the "abnormal" column for debugging
print(heart_data.head())
print(heart_data.tail())

X = heart_data.drop(columns=["condition"])  # Features
y = heart_data["condition"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
classifier = DecisionTreeClassifier(random_state=42)
classifier.fit(X_train, y_train)
predictions = classifier.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print("\nAccuracy:", accuracy)
joblib.dump(classifier, 'heart_rate_classifier.pkl')
