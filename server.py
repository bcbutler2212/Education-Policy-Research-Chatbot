from flask import Flask, request, jsonify, render_template_string, send_file
import subprocess
import sys
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/styles.css')
def styles():
    """Serve the CSS file"""
    try:
        return send_file('styles.css', mimetype='text/css')
    except FileNotFoundError:
        return "styles.css not found", 404

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    try:
        return send_file('script.js', mimetype='application/javascript')
    except FileNotFoundError:
        return "script.js not found", 404

@app.route('/query', methods=['POST'])
def query():
    """Handle chat queries by calling query.py"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Try to call query.py first, fallback to test_query.py if API key is missing
        try:
            result = subprocess.run(
                [sys.executable, 'query.py', message],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=60
            )

            # If query.py fails due to missing API key, use test version
            if result.returncode != 0 and "ANTHROPIC_API_KEY" in result.stderr:
                print("ANTHROPIC_API_KEY not found, using test mode")
                result = subprocess.run(
                    [sys.executable, 'test_query.py', message],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    timeout=30
                )
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Query timed out'}), 500

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else 'Unknown error occurred'
            return jsonify({'error': f'Query failed: {error_msg}'}), 500

        response_text = result.stdout.strip()

        return jsonify({'response': response_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)