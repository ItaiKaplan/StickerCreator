import shutil
import os
import requests
import sticker_generator
from fastapi import FastAPI, Form
import uvicorn

app = FastAPI()

@app.get("/hello")
async def hello():
    return {"message": "Hello World"}


@app.post("/video-to-sticker/")
async def create_sticker_as_base64(video_url: str = Form(...), frame_time_ms: int = Form(...)):
    print("Starting")
    video_path = f"Videos/{os.path.basename(video_url)}"

    # Download the video file from the URL
    response = requests.get(video_url, stream=True)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(response.raw, buffer)

    output_sticker_path = f"Stickers/{os.path.splitext(os.path.basename(video_url))[0]}.webp"

    # Call the video_to_sticker_base64 function
    sticker_base64 = sticker_generator.video_to_sticker_base64(video_path, frame_time_ms, output_sticker_path)
    return {"sticker_base64": sticker_base64}


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8086))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
