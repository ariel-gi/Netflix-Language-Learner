import os
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field
from typing import List
from groq import Groq
import instructor
import json
import sys

if sys.stdout.encoding != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')

api_key = "ADD_YOUR_OWN_KEY"
app = Flask(__name__)

@app.route('/api', methods=['POST'])

def handle_request():
    data = request.json
    # Process the data and return a response
    subtitle_list = data.get("captions")
    target_language = data.get("language")
    print("Received subtitles:", subtitle_list, flush=True)
    print("Received language:", target_language, flush=True)

    response = groqRequest(subtitle_list, target_language)

    print(response)
    
    response_data = jsonify(response)
    response_data.headers['Content-Type'] = 'application/json'

    return response_data

# groq request-----------------------------------------------------------------------------

def groqRequest (captions, native_language):

    class CaptionChunks(BaseModel):
        chunked: List[List[str]] = Field(..., description="A list of lists of chunked captions")
        translated_chunks: List[List[str]] = Field(..., description="A list of lists of translated chunked captions")


    client = Groq(
        api_key=api_key,
    )

    client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

    content = (
    f"For a hover-over language learning feature, please perform the following tasks with the provided captions:\n"
    f"1. Chunk each caption into smaller, meaningful segments (chunks). Most of the individual words should be chunked on their own.\n"
    f"2. Only group two or more words into a single chunk if they form a phrase that must stay together when translated into {native_language}.\n"
    f"3. Store each list of chunks into a master list called `chunked`, where each item corresponds to the chunks of one caption.\n"
    f"4. Translate each chunk into {native_language}.\n"
    f"5. Store each list of translated chunks into another master list called `translated_chunks`, where each item corresponds to the translated chunks of the same caption.\n"
    f"Here are the captions:\n{' | '.join(captions)}"
)

    resp = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        response_model=CaptionChunks,
    )
    return resp.model_dump_json(indent=2)

 ## end -----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run()
