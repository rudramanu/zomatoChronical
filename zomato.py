from flask import Flask, request,jsonify
import pickle
import uuid

app=Flask(__name__)

menu={}
orders={}

def load_data():
    global menu,orders
    try:
        with open("menu.pickle","rb") as file:
            menu=pickle.load(file)
        with open("orders.pickle","rb") as file:
            orders=pickle.load(file)
    except FileNotFoundError:
        menu={}
        orders={}        

def save_data():
    with open("menu.pickle","wb") as file:
        pickle.dump(menu,file)
    with open("orders.pickle","wb") as file:
        pickle.dump(orders,file)    

@app.route("/")
def hello_server():
    return "Hello Server"

@app.route("/menu", methods=["GET"])
def get_menu():
    return jsonify(menu)

@app.route("/menu",methods=["POST"])
def add_dish():
    dish=request.json
    dish_id=str(uuid.uuid4())
    dish["id"]=dish_id
    dish["available"]="yes"
    menu[dish_id]=dish
    print(dish_id)
    save_data()
    return jsonify({"message":"New Dish Added!","dish":dish}),201

@app.route("/menu/<dish_id>",methods=["DELETE"])
def remove_dish(dish_id):
    if dish_id in menu:
        del menu[dish_id]
        save_data()
        return jsonify({"message":"Dish removed"}),200
    return jsonify({"message":"Dish not found"}),404

@app.route("/menu/<dish_id>",methods=["PUT"])
def update_dish(dish_id):
    if dish_id in menu:
        request.json["id"]=dish_id
        menu[dish_id]=request.json
        save_data()
        return jsonify({"message":"Dish updated"}),200
    return jsonify({"message":"Dish not found"}),404

@app.route("/order",methods=["POST"])
def place_order():
    order = request.json
    customer_name = order.get("customer_name")
    dish_id = order["dish"]
    if not customer_name or not dish_id:
        return jsonify({"error": "Invalid order data."}), 400

    order_id = len(orders) + 1
    order["status"] = "received"
    order["id"] = order_id

    if dish_id not in menu:
            return jsonify({"error": "Invalid dish in the order."}), 400

    orders[order_id] = order
    return jsonify({"message": "Order placed!", "order": order}), 201

@app.route("/order/<int:order_id>",methods=["PUT"])
def update_order(order_id):
    if order_id in orders:
        request.json["id"]=order_id
        orders[order_id]=request.json
        save_data()
        return jsonify({"message":"Order updated"}),200
    return jsonify({"message":"Order not found"}),404




@app.route("/order", methods=["GET"])
def get_orders():
    return jsonify(orders)

@app.route("/exit", methods=["POST"])
def exit_app():
    menu.clear()
    orders.clear()
    return jsonify({"message": "Application closed."}), 200

if __name__ == '__main__':
    app.run(port=3000)