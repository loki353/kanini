import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import joblib

df = pd.read_csv("synthetic_health_data.csv")

le_gender = LabelEncoder()
le_condition = LabelEncoder()
le_risk = LabelEncoder()

df["Gender"] = le_gender.fit_transform(df["Gender"])
df["Condition"] = le_condition.fit_transform(df["Condition"])
df["Risk"] = le_risk.fit_transform(df["Risk"])

X = df.drop("Risk", axis=1)
y = df["Risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = XGBClassifier()
model.fit(X_train, y_train)

joblib.dump(model, "triage_model.pkl")
joblib.dump(le_gender, "le_gender.pkl")
joblib.dump(le_condition, "le_condition.pkl")
joblib.dump(le_risk, "le_risk.pkl")

print("Model files created successfully!")
