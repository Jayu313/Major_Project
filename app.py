from flask import Flask, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "livvra_secret_key"

CORS(app, supports_credentials=True)

# -------------------------------------------------
# TEMP IN-MEMORY USERS (DEV ONLY)
# -------------------------------------------------
users = []
admins = {
    "admin@livvra.com": {
        "email": "admin@livvra.com",
        "password": "admin",
        "first_name": "Admin",
        "last_name": ""
    }
}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def find_user(email):
    for u in users:
        if u["email"] == email:
            return u
    return admins.get(email)

def logged_in():
    return "email" in session

# -------------------------------------------------
# REGISTER
# -------------------------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if find_user(data["email"]):
        return jsonify({"error": "Email already exists"}), 400

    users.append({
        "email": data["email"],
        "password": data["password"],
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", "")
    })

    return jsonify({
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", "")
    })

# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = find_user(data.get("email"))

    if not user or user["password"] != data["password"]:
        return jsonify({"error": "Invalid credentials"}), 401

    session["email"] = user["email"]

    return jsonify({
        "first_name": user["first_name"],
        "last_name": user["last_name"]
    })

# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

# -------------------------------------------------
# SESSION CHECK
# -------------------------------------------------
@app.route("/me")
def me():
    if not logged_in():
        return jsonify({"logged_in": False})

    user = find_user(session["email"])
    return jsonify({
        "logged_in": True,
        "first_name": user["first_name"],
        "last_name": user["last_name"]
    })

# -------------------------------------------------
# PREDICT
# -------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if not logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    current_price = int(data["current_price"])
    years = int(data["years"])

    predicted = int(current_price * 1.12)
    percent = round(((predicted - current_price) / current_price) * 100)

    if percent > 10:
        status = "BUY"
    elif percent >= 4:
        status = "HOLD"
    else:
        status = "SELL"

    forecast = []
    value = predicted
    for _ in range(years):
        value = int(value * 1.10)
        forecast.append(value)

    return jsonify({
        "current": current_price,
        "predicted": predicted,
        "percent": percent,
        "status": status,
        "forecast": forecast
    })

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
