import os
import json
import requests
import re
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # This handles the "Preflight" check browsers do before the real request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # 1. READ THE REQUEST BODY
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            base64_image = data.get('image')

            # 2. CALL OPENAI
            api_key = os.environ.get("OPENAI_API_KEY")
            payload = {
                "model": "gpt-4.1-mini",
                "messages": [{
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "Identify this insect and return raw JSON..." },
                        { "type": "image_url", "image_url": { "url": f"data:image/jpeg;base64,{base64_image}" } }
                    ]
                }],
                "max_tokens": 500
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            # 3. EXTRACT AND CLEAN THE DATA
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            cleaned = re.sub(r'```json|```', '', content).strip()

            # 4. SEND THE SUCCESS RESPONSE
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Essential for "Failed to fetch"
            self.end_headers()
            self.wfile.write(cleaned.encode('utf-8'))

        except Exception as e:
            # SEND ERROR RESPONSE
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_msg = json.dumps({"error": str(e)})
            self.wfile.write(error_msg.encode('utf-8'))
