from fastapi import FastAPI

app = FastAPI(title="Todo API", description="Clean Architecture Todo API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API! App is running successfully."}
