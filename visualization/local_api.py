from flask import Flask, jsonify, request, send_file
import json
import time

app = Flask(__name__)
received_data = []
lastest_data = None

@app.route('/api/ie212_o11_group7/endpoint', methods=['GET', 'POST'])
def collect_reviews_data():
    global lastest_data
    if request.method == 'GET':
        try:
            # Convert the JSON string to a Python object
            json_data = json.loads(lastest_data)

            # Save the converted data to a temporary JSON file
            temp_file_path = 'temp_latest_data.json'
            with open(temp_file_path, 'w') as json_file:
                json.dump(json_data, json_file)

            # Send the file as a response with appropriate headers
            return send_file(temp_file_path, as_attachment=False, mimetype='application/json')
        except Exception as e:
            return jsonify({"error": str(e)})
    elif request.method == 'POST':
        try:
            data = request.get_json()
            lastest_data = data
            received_data.append(data)

            # temp_file_path = 'received_data.json'
            # with open(temp_file_path, 'w') as json_file:
            #     json.dump(received_data, json_file)

            return jsonify({"message": "Data received successfully"})
        except Exception as e:
            return jsonify({"error": str(e)})
        
received_pos_neg_data = []

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
