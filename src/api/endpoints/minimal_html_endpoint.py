# /src/api/endpoints/minimal_html_endpoint.py
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Kafka Endpoint Base</title>
</head>
<body>
    <h1>Consumer & Producer Base Endpoint</h1>
    <p>Este HTML sirve como placeholder mientras se integran los microservicios Kafka.</p>
</body>
</html>
"""

@app.route('/html', methods=['GET'])
def serve_html():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# Backlog siguiente: "Integrar endpoint con Kafka consumer y producer funcional"

