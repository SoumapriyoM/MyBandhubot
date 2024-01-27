import requests

def get_text_emotion(text):
    url = "https://twinword-emotion-analysis-v1.p.rapidapi.com/analyze/"
    payload = { "text": text }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "f57f8e9a13mshc8dbe8587fc090cp1e6b8cjsndfb06d21fb13",
        "X-RapidAPI-Host": "twinword-emotion-analysis-v1.p.rapidapi.com"
    }
    response = requests.post(url, data=payload, headers=headers)
    return response.json()['emotions_detected']

# Example usage
text = "I want to die"
emotions_detected = get_text_emotion(text)
print("Emotions Detected:", emotions_detected)
