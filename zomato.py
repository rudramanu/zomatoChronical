from flask import Flask, request,jsonify
from flask_cors import CORS

from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from bson import ObjectId
from bson import json_util


app=Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://rudramanu:rudramanu@cluster0.ddgpgik.mongodb.net/flaskdatabase?retryWrites=true&w=majority'



mongo = PyMongo(app)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app,cors_allowed_origins='*')

@app.route("/")
def hello_server():
    return "Hello Server"

@app.route("/menu", methods=["GET"])
def get_menu():
    collection = mongo.db.flaskdatabase  
    data = list(collection.find())
    return json_util.dumps(data)

@app.route("/menu",methods=["POST"])
def add_dish():
    dish=request.json
    
    dish["_id"]=str(ObjectId()) 
    dish["available"]="yes"
    
    collection=mongo.db.flaskdatabase
    collection.insert_one(dish)
    return jsonify({"message":"New Dish Added!","dish":dish}),201
    

@app.route("/menu/<dish_id>",methods=["DELETE"])
def remove_dish(dish_id):
    collection = mongo.db.flaskdatabase
    result = collection.delete_one({'_id': dish_id})
    
    if result.deleted_count > 0:
        return jsonify({"message": "Dish removed"}), 200
    else:
        return jsonify({"message": "Dish not found"}), 404

@app.route("/menu/<dish_id>",methods=["PUT"])
def update_dish(dish_id):

    collection = mongo.db.flaskdatabase
    
    updated_data = request.json
    updated_data["_id"] = dish_id
    
    result = collection.update_one({'_id': dish_id}, {'$set': updated_data})
    
    if result.modified_count > 0:
        return jsonify({"message": "Dish updated"}), 200
    else:
        return jsonify({"message": "Dish not found"}), 404

@app.route("/order",methods=["POST"])
def place_order():
    order = request.json
    customer_name = order.get("customer_name")
    dish_id = order["dish"]
    order["status"] = "received"

    if not customer_name or not dish_id:
        return jsonify({"error": "Invalid order data."}), 400

    collection = mongo.db.orders

    if not mongo.db.flaskdatabase.find_one({"_id": dish_id}):
        return jsonify({"error": "Invalid dish in the order."}), 400

    order_id = str(ObjectId())
    order["_id"] = order_id

    collection.insert_one(order)

    return jsonify({"message": "Order placed!", "order": order}), 201

@app.route("/order/<order_id>",methods=["PUT"])
def update_order(order_id):
    collection = mongo.db.orders
    
    updated_data = request.json
    updated_data["_id"] = order_id
    
    result = collection.update_one({'_id': order_id}, {'$set': updated_data})
    
    if result.modified_count > 0:
        return jsonify({"message": "Order updated"}), 200
    else:
        return jsonify({"message": "Order not found"}), 404

@app.route("/order", methods=["GET"])
def get_orders():
    collection = mongo.db.orders  
    data = list(collection.find())
    return json_util.dumps(data)

@app.route("/exit", methods=["POST"])
def exit_app():
    return jsonify({"message": "Application closed."}), 200
# ==============web socket code for chat====================

@socketio.on('message')
def handle_message(message):
    chat_responses = {
        "1": "Our operation hours are from 9:00 AM to 10:00 PM.",
        "2": "Please provide your order ID, and I'll check the status for you.",
        "Thank you":"Thank you, Please visit again",
        "Thanks":"Thank you, Please visit again",
        "thank you":"Thank you, Please visit again",
        "thanks":"Thank you, Please visit again",
    }
    for key in chat_responses:
        if key == message:
            response=chat_responses[key]
            return emit('receive', response)
    else:
        collection = mongo.db.orders  
        data = collection.find_one({"_id":message})
        status="status"
        if data is not None:
            response = f"Your order is {data[status]}"
            emit('receive', response)
        else:
            response = chat_responses.get(message, "I'm sorry, but I don't have an answer for that.")
            emit('receive', response)  
if __name__ == '__main__':
    socketio.run(app, debug=True) 