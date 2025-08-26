# Face Test Service

This folder contains a minimal web service for testing students with a simple form of biometric authentication. The service does **not** implement real facial recognition; it only compares hashed image data for demonstration purposes.

## Running

```
python3 face_service.py
```

The service listens on port `8000` and provides these endpoints:

- `POST /register` – register a student with `{ "id": "student1", "face": "<base64 image>" }`.
- `POST /login` – authenticate a student with the same payload.
- `GET /test?id=<student>` – fetch test questions.
- `POST /submit` – submit answers with `{ "id": "student1", "answers": {...} }`.

Data is stored under `data/`.
