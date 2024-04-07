from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pipeline import ChatbotPipeline
import time
import requests
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

api_key1 = os.getenv('api_key1')
api_key2 = os.getenv('api_key2')

if api_key1 is None or api_key2 is None:
    raise EnvironmentError("One or more required environment variables are missing.")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, you can also specify specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

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
    answer = pipeline.generate_answer(pattern.pattern)
    try:
        # Generate an answer using the chatbot pipeline
        # Get emotion for the input text
        emotion = pipeline.get_emotion(pattern.pattern, api_key2)

        return {"answer": answer, "emotion": emotion}
    except Exception as e:
        emotion = "Neutral"
        return {"answer": answer, "emotion": emotion}

@app.get("/recommendations")
async def get_music_recommendations(emotion: str):
    try:
        # Replace 'YOUR_LASTFM_API_KEY' with your Last.fm API key
        limit = 5  # You can adjust the limit as needed

        # Make a request to Last.fm API to get top tracks based on the provided emotion
        lastfm_url = f'http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag={emotion}&api_key={api_key1}&format=json&limit={limit}'
        response = requests.get(lastfm_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()
        tracks = data.get('tracks', {}).get('track', [])

        # Extract relevant information for each track
        recommendation = []
        for track in tracks:
            track_name = track.get('name', '')
            artist_name = track.get('artist', {}).get('name', '')
            image_url = track.get('image', [])[2].get('#text', '')  # Use a higher resolution image
            track_url = track.get('url', '')

            recommendation.append({
                'track_name': track_name,
                'artist_name': artist_name,
                'image_url': image_url,
                'track_url': track_url
            })

        return {"recommendations": recommendation}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to get music recommendations: {str(e)}")
