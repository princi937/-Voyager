"""
Travel Planner Agent — Flask Application Entry Point
"""
import uuid
from dotenv import load_dotenv

load_dotenv()
import os
print("URL =", os.getenv("IBM_WATSONX_URL"))
print("API =", os.getenv("IBM_API_KEY"))
print("PROJECT =", os.getenv("IBM_PROJECT_ID"))
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for,
)
from modules import data_store as ds
from modules import watsonx_client as wx
from modules import prompt_builder as pb

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

# ── Session helpers ──────────────────────────────────────────────────────────
def get_sid() -> str:
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return session["sid"]


# ── Pages ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    sid = get_sid()
    trips = ds.get_trips(sid)
    profiles = ds.get_profiles(sid)
    return render_template("dashboard.html", trips=trips, profiles=profiles)


@app.route("/chat")
def chat_page():
    sid = get_sid()
    history = ds.get_chat_history(sid)
    return render_template("chat.html", history=history)


@app.route("/itinerary")
def itinerary_page():
    return render_template("itinerary.html")


@app.route("/destinations")
def destinations_page():
    return render_template("destinations.html")


@app.route("/budget")
def budget_page():
    return render_template("budget.html")


@app.route("/profiles")
def profiles_page():
    sid = get_sid()
    profiles = ds.get_profiles(sid)
    return render_template("profiles.html", profiles=profiles)


@app.route("/history")
def history_page():
    sid = get_sid()
    trips = ds.get_trips(sid)
    return render_template("history.html", trips=trips)


# ── API: Chat ────────────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    sid = get_sid()
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    ds.append_message(sid, "user", user_message)
    history = ds.get_chat_history(sid)

    try:
        reply = wx.chat(history)
    except Exception as exc:
        return jsonify({"error": f"AI service error: {exc}"}), 502

    ds.append_message(sid, "assistant", reply)
    return jsonify({"reply": reply})


@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    ds.clear_chat(get_sid())
    return jsonify({"status": "cleared"})


# ── API: Itinerary ────────────────────────────────────────────────────────────
@app.route("/api/itinerary", methods=["POST"])
def api_itinerary():
    sid = get_sid()
    data = request.get_json(force=True)

    required = ["destination", "days", "budget"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    prompt = pb.build_itinerary_prompt(data)
    ds.append_message(sid, "user", prompt)

    try:
        reply = wx.chat(ds.get_chat_history(sid))
    except Exception as exc:
        return jsonify({"error": f"AI service error: {exc}"}), 502

    ds.append_message(sid, "assistant", reply)

    # Auto-save trip
    trip_id = ds.save_trip(sid, {
        "destination": data.get("destination"),
        "days": data.get("days"),
        "budget": data.get("budget"),
        "currency": data.get("currency", "INR"),
        "travelers": data.get("travelers", ""),
        "travel_style": data.get("travel_style", ""),
        "itinerary": reply,
    })
    return jsonify({"itinerary": reply, "trip_id": trip_id})


# ── API: Destination Recommendations ─────────────────────────────────────────
@app.route("/api/destinations", methods=["POST"])
def api_destinations():
    sid = get_sid()
    data = request.get_json(force=True)
    prompt = pb.build_destination_prompt(data)
    ds.append_message(sid, "user", prompt)

    try:
        reply = wx.chat(ds.get_chat_history(sid))
    except Exception as exc:
        return jsonify({"error": f"AI service error: {exc}"}), 502

    ds.append_message(sid, "assistant", reply)
    return jsonify({"recommendations": reply})


# ── API: Budget Estimate ──────────────────────────────────────────────────────
@app.route("/api/budget", methods=["POST"])
def api_budget():
    sid = get_sid()
    data = request.get_json(force=True)

    if not data.get("destination"):
        return jsonify({"error": "Destination is required."}), 400

    prompt = pb.build_budget_prompt(data)
    ds.append_message(sid, "user", prompt)

    try:
        reply = wx.chat(ds.get_chat_history(sid))
    except Exception as exc:
        return jsonify({"error": f"AI service error: {exc}"}), 502

    ds.append_message(sid, "assistant", reply)
    return jsonify({"estimate": reply})


# ── API: Traveler Profiles ────────────────────────────────────────────────────
@app.route("/api/profiles", methods=["GET"])
def api_profiles_get():
    return jsonify(ds.get_profiles(get_sid()))


@app.route("/api/profiles", methods=["POST"])
def api_profiles_post():
    data = request.get_json(force=True)
    required = ["name", "age", "travel_type"]
    missing = [f for f in required if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    profile_id = ds.save_profile(get_sid(), data)
    return jsonify({"id": profile_id, "status": "saved"})


@app.route("/api/profiles/<profile_id>", methods=["DELETE"])
def api_profiles_delete(profile_id: str):
    removed = ds.delete_profile(get_sid(), profile_id)
    if not removed:
        return jsonify({"error": "Profile not found."}), 404
    return jsonify({"status": "deleted"})


# ── API: Trips ────────────────────────────────────────────────────────────────
@app.route("/api/trips", methods=["GET"])
def api_trips_get():
    return jsonify(ds.get_trips(get_sid()))


@app.route("/api/trips/<trip_id>", methods=["DELETE"])
def api_trips_delete(trip_id: str):
    removed = ds.delete_trip(get_sid(), trip_id)
    if not removed:
        return jsonify({"error": "Trip not found."}), 404
    return jsonify({"status": "deleted"})


# ── API: Weather placeholder ──────────────────────────────────────────────────
@app.route("/api/weather", methods=["POST"])
def api_weather():
    """
    Placeholder — connect to OpenWeatherMap or IMD API here.
    For now returns a mock response and asks the AI for tips.
    """
    data = request.get_json(force=True)
    destination = data.get("destination", "")
    month = data.get("month", "")

    prompt = (
        f"What is the typical weather in {destination} during {month}? "
        "Provide temperature range, precipitation, what to wear, and any "
        "weather-related travel warnings. Be concise (5-7 lines)."
    )
    sid = get_sid()
    ds.append_message(sid, "user", prompt)

    try:
        reply = wx.chat(ds.get_chat_history(sid))
    except Exception as exc:
        return jsonify({"error": f"AI service error: {exc}"}), 502

    ds.append_message(sid, "assistant", reply)
    return jsonify({"weather_info": reply, "source": "AI-generated (connect real API for live data)"})


if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", 5000))
    host = os.environ.get("APP_HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    app.run(host=host, port=port, debug=debug)
