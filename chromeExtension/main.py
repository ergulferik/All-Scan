from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/get_data', methods=['POST'])
def get_data():
    if request.method == 'POST':
        content = request.json.get('content')
        url = request.json.get('url')
        print("Sayfa İçeriği:", content)
        print("Sayfa URL'si:", url)
        return jsonify({'message': 'osman ananı sikeyim'})
    else:
        return 'Only POST requests are allowed for this endpoint!', 405

if __name__ == '__main__':
    app.run(debug=True)
