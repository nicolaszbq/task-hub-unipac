from flask import Flask, jsonify, make_response, request


app = Flask(__name__)

# Ping-Pong API TEST
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"status": "pong", "message":"API is running!"}), 200

if __name__ == '__main__':
    app.run(debug=True)