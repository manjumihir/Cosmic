from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

@app.route("/")
def root():
    return jsonify({
        "message": "Welcome to the Astrology API. Use /api/astro or /api/location for data."
    })

@app.route("/api/astro", methods=["POST"])
def calculate_astrology():
    data = request.json  # Parse incoming JSON data

    # Extract input fields
    name = data.get("name")
    dob = data.get("dateOfBirth")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # Validate input
    if not all([name, dob, latitude, longitude]):
        return jsonify({"error": "All fields (name, dateOfBirth, latitude, longitude) are required"}), 400

    try:
        # Convert latitude and longitude to floats for calculation
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({"error": "Latitude and Longitude must be valid numbers"}), 400

    # Placeholder for your astrology calculation logic (static response for now)
    result = {
        "name": name,
        "dob": dob,
        "latitude": latitude,
        "longitude": longitude,
        "sun_degree": 120.5,  # Replace with actual calculation
        "moon_degree": 240.3  # Replace with actual calculation
    }

    return jsonify(result)  # Return the calculated result

if __name__ == "__main__":
    app.run(port=5001)