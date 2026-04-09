import os
import json
import requests
import re

# Vercel recognizes a function named 'handler' automatically
def handler(request):
    # --- 1. CORS SECURITY ---
    allowed_origin = "https://hexascope.lovable.app"
    headers = {
        "Access-Control-Allow-Origin": allowed_origin,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    # Handle browser security checks
    if request.method == 'OPTIONS':
        return {"statusCode": 200, "headers": headers, "body": ""}

    try:
        # --- 2. GET THE IMAGE DATA ---
        # We use request.get_json() which is safer than reading a 'file'
        data = request.get_json()
        base64_image = data.get('image')

        if not base64_image:
            return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": "No image found"})}

        # --- 3. CALL OPENAI ---
        api_key = os.environ.get("OPENAI_API_KEY")
        payload = {
            "model": "gpt-4.1-mini",
            "messages": [{
                "role": "user",
                "content": [
                    { "type": "text", "text": "Identify the insect... (Your full prompt here)" },
                    { "type": "image_url", "image_url": { "url": f"data:image/jpeg;base64,{base64_image}" } }
                ]
            }],
            "max_tokens": 500
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload
        )

        # --- 4. RETURN THE RESULT ---
        content = response.json()['choices'][0]['message']['content']
        cleaned = re.sub(r'```json|```', '', content).strip()

        return {
            "statusCode": 200,
            "headers": headers,
            "body": cleaned
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
