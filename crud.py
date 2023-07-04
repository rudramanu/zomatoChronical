from flask import Flask, request, jsonify

app = Flask(__name__)

# Create an empty dictionary to store data
data = {
    "name":"Rudra"
}

@app.route('/read', methods=['GET'])
def read():
    return jsonify(data)

@app.route('/create', methods=['POST'])
def create():
    key = request.form.get('key')
    value = request.form.get('value')

    if key and value:
        data[key] = value
        return jsonify({'message': f'Entry with key "{key}" created.'})
    else:
        return jsonify({'error': 'Invalid data. Both key and value are required.'}), 400


@app.route('/update', methods=['POST'])
def update():
    key = request.form.get('key')
    value = request.form.get('value')

    if key in data:
        data[key] = value
        return jsonify({'message': f'Value of entry with key "{key}" updated.'})
    else:
        return jsonify({'error': f'Entry with key "{key}" not found.'}), 404

    
@app.route('/delete', methods=['POST'])
def delete():
    key = request.form.get('key')

    if key in data:
        del data[key]
        return jsonify({'message': f'Entry with key "{key}" deleted.'})
    else:
        return jsonify({'error': f'Entry with key "{key}" not found.'}), 404


if __name__ == '__main__':
    app.run()
