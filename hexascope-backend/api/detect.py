import os
import json
import requests
import re

def handler(request):
    # --- 1. HANDLE CORS MANUALLY ---
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': ''
        }

    try:
        # --- 2. GET DATA ---
        # request.get_json() is the most stable way on Vercel
        request_json = request.get_json(silent=True)
        if not request_json:
            return {'statusCode': 400, 'body': 'No JSON body found'}
            
        base64_image = request_json.get('image')
        
        # --- 3. CALL OPENAI ---
        api_key = os.environ.get("OPENAI_API_KEY")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini", # Using mini to ensure it stays cheap and fast
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Identify this insect and return raw JSON..."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                "max_tokens": 500
            }
        )

        # --- 4. RETURN RESPONSE ---
        res_data = response.json()
        content = res_data['choices'][0]['message']['content']
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
