import os
import json
import requests
import re

def handler(request):
    # 1. Handle Preflight (OPTIONS)
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': ''
        }

    try:
        # 2. Parse Image
        data = request.get_json()
        base64_image = data.get('image')

        # 3. OpenAI Call
        api_key = os.environ.get("OPENAI_API_KEY")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Identify this insect and return raw JSON..."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            }
        )

        # 4. Return Clean JSON
        content = response.json()['choices'][0]['message']['content']
        cleaned = re.sub(r'```json|```', '', content).strip()
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': cleaned
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({"error": str(e)})
        }
