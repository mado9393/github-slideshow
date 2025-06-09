import http.server
import socketserver
import json
import base64
import hashlib
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FACES_DB = os.path.join(DATA_DIR, 'faces.json')
TESTS_DB = os.path.join(DATA_DIR, 'tests.json')
RESULTS_DB = os.path.join(DATA_DIR, 'results.json')

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

class Handler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/test'):
            parts = self.path.split('?')
            if len(parts) > 1:
                params = dict(p.split('=') for p in parts[1].split('&') if '=' in p)
                sid = params.get('id')
                tests = load_json(TESTS_DB, [])
                self._set_headers()
                self.wfile.write(json.dumps({'tests': tests}).encode())
                return
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
            return

        if self.path == '/register':
            sid = data.get('id')
            face = data.get('face')
            if not sid or not face:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing id or face'}).encode())
                return
            faces = load_json(FACES_DB, {})
            faces[sid] = hashlib.sha256(base64.b64decode(face)).hexdigest()
            save_json(FACES_DB, faces)
            self._set_headers()
            self.wfile.write(json.dumps({'status': 'registered'}).encode())
            return

        if self.path == '/login':
            sid = data.get('id')
            face = data.get('face')
            faces = load_json(FACES_DB, {})
            if sid in faces:
                expected = faces[sid]
                current = hashlib.sha256(base64.b64decode(face)).hexdigest()
                if expected == current:
                    self._set_headers()
                    self.wfile.write(json.dumps({'status': 'authenticated'}).encode())
                    return
            self._set_headers(401)
            self.wfile.write(json.dumps({'error': 'authentication failed'}).encode())
            return

        if self.path == '/submit':
            sid = data.get('id')
            answers = data.get('answers')
            if not sid or answers is None:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing id or answers'}).encode())
                return
            results = load_json(RESULTS_DB, {})
            results[sid] = answers
            save_json(RESULTS_DB, results)
            self._set_headers()
            self.wfile.write(json.dumps({'status': 'submitted'}).encode())
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())

if __name__ == '__main__':
    port = 8000
    with socketserver.TCPServer(('', port), Handler) as httpd:
        print(f'Serving on port {port}')
        httpd.serve_forever()
