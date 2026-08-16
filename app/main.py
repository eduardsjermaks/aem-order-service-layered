from fastapi import FastAPI

app = FastAPI(title="AEM Order Service")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
