import pandas as pd
import random

def generate_synthetic_data(n=5000):
    data = []

    for _ in range(n):
        age = random.randint(18, 90)
        gender = random.choice(["Male", "Female"])
        bp = random.randint(90, 200)
        hr = random.randint(60, 150)
        temp = round(random.uniform(97.0, 104.0), 1)
        condition = random.choice(["None", "Diabetes", "Hypertension", "Asthma"])

        if bp > 180 or hr > 130:
            risk = "High"
        elif bp > 150 or temp > 101:
            risk = "Medium"
        else:
            risk = "Low"

        data.append([age, gender, bp, hr, temp, condition, risk])

    columns = ["Age", "Gender", "BloodPressure", "HeartRate", "Temperature", "Condition", "Risk"]
    return pd.DataFrame(data, columns=columns)


if __name__ == "__main__":
    df = generate_synthetic_data()
    df.to_csv("synthetic_health_data.csv", index=False)
    print("Synthetic dataset created!")
