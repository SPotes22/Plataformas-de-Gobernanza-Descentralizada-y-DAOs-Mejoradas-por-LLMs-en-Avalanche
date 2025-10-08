from fastapi import FastAPI
import joblib, uvicorn
import numpy as np

app = FastAPI()
model = joblib.load("model.pkl")  # trained previously

@app.post("/predict")
def predict(payload: dict):
    # Map payload to features: adjust to your schema
    X = np.array([[float(v) for v in payload.values()]])
    pred = model.predict_proba(X)[0, 1]
    return {"score": float(pred)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
