from fastapi import FastAPI

app = FastAPI()

# Add your endpoints here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 