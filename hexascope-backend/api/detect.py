import os
import json
import requests
import re
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Mandatory for CORS 'Failed to Fetch' errors
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # 1. Handle Headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            # 2. Get the Data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_json = json.loads(post_data)
            
            base64_image = request_json.get('image')
            if not base64_image:
                self.wfile.write(json.dumps({"error": "No image found"}).encode())
                return

            # 3. Call OpenAI
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
                    }],
                    "max_tokens": 500
                }
            )

            # 4. Clean and Return
            res_data = response.json()
            content = res_data['choices'][0]['message']['content']
            cleaned = re.sub(r'```json|```', '', content).strip()
            
            self.wfile.write(cleaned.encode('utf-8'))

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
