import http.server
import socketserver
import json
import os
import datetime

# --- CONFIGURATION ---
PORT = 8000
DATA_FILE = 'data/registrations.json'
STATIC_DIR = 'static'

# --- DATA HANDLING (Simulated Database) ---

def load_registrations():
    """Loads all registrations from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return [] # Return empty list if file is empty or corrupted

def save_registrations(data):
    """Saves the registrations data to the JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- CUSTOM REQUEST HANDLER ---

class RegistrationServer(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        """Handles serving static files and the main HTML page."""
        
        # 1. Handle API GET request for data
        if self.path == '/api/registrations':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = load_registrations()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        # 2. Serve static files (HTML, CSS, JS)
        if self.path == '/':
            self.path = '/templates/index.html'
            
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Handles new participant registration submissions."""
        if self.path == '/api/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Decode JSON data from the frontend
                new_reg = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_json_response(400, {"message": "Invalid JSON data."})
                return

            # --- Backend Validation and Logic ---
            name = new_reg.get('name', '').strip()
            email = new_reg.get('email', '').strip()
            event = new_reg.get('event', '').strip()
            
            if not all([name, email, event]):
                self._send_json_response(400, {"message": "All fields are required."})
                return

            registrations = load_registrations()
            
            # Check for duplicate email
            if any(reg['email'].lower() == email.lower() for reg in registrations):
                self._send_json_response(409, {"message": f"Email '{email}' is already registered."})
                return

            # Create and save new record
            new_record = {
                "id": len(registrations) + 1,
                "name": name,
                "email": email,
                "event": event,
                "registration_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            registrations.append(new_record)
            save_registrations(registrations)

            self._send_json_response(201, {"message": "Registration successful!", "record": new_record})
            
        else:
            self._send_json_response(404, {"message": "Endpoint not found."})

    def _send_json_response(self, status_code, data):
        """Helper function to send a JSON response."""
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

# --- SERVER RUNNER ---

if __name__ == "__main__":
    print(f"Starting server on port {PORT}...")
    
    # Set the current directory to the project root for file serving
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = RegistrationServer
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")