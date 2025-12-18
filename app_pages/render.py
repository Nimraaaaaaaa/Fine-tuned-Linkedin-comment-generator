services:
  - type: web
    name: fastapi-backend
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app:app --host 0.0.0.0 --port 8000"
    envVars:
      - key: OPENAI_API_KEY
        value: your_openai_key_here
