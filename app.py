from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pipeline import ChatbotPipeline

app = FastAPI()

# Mount the "static" directory to serve static files (CSS and JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the pre-trained chatbot pipeline
pipeline = ChatbotPipeline.load_pipeline(
    model_path='model_jar/model.h5',
    tokenizer_path='model_jar/tokenizer.pkl',
    pipeline_path='model_jar/pipeline.pkl'
)

# Define the HTML endpoint
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("static/index.html")

# Define the API endpoint for chatbot predictions
class PatternInput(BaseModel):
    pattern: str

@app.post("/predict")
async def predict(pattern: PatternInput):
    try:
        # Generate an answer using the chatbot pipeline
        answer = pipeline.generate_answer(pattern.pattern)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
