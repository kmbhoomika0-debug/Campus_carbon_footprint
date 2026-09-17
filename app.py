from flask import Flask, render_template, request, jsonify
import json
import urllib.request
import urllib.error

app = Flask(__name__)


# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================
# CALCULATOR PAGE
# =========================================

@app.route("/calculator")
def calculator():
    return render_template("calculator.html")


# =========================================
# CARBON CALCULATION
# =========================================

@app.route("/calculate", methods=["POST"])
def calculate():

    # -------------------------------------
    # GET INPUT VALUES
    # -------------------------------------

    electricity = float(request.form.get("electricity") or 0)
    petrol = float(request.form.get("petrol") or 0)
    diesel = float(request.form.get("diesel") or 0)

    bus_km = float(request.form.get("bus_km") or 0)
    vehicle_km = float(request.form.get("vehicle_km") or 0)

    general_waste = float(request.form.get("general_waste") or 0)
    recycled_waste = float(request.form.get("recycled_waste") or 0)

    water = float(request.form.get("water") or 0)


    # -------------------------------------
    # EMISSION FACTORS
    # -------------------------------------

    electricity_factor = 0.716

    petrol_factor = 2.31
    diesel_factor = 2.68

    bus_factor = 0.8
    vehicle_factor = 0.21

    general_waste_factor = 0.5
    recycled_waste_factor = 0.1

    water_factor = 0.0003


    # -------------------------------------
    # EMISSIONS
    # -------------------------------------

    electricity_emissions = (
        electricity * electricity_factor
    )

    petrol_emissions = (
        petrol * petrol_factor
    )

    diesel_emissions = (
        diesel * diesel_factor
    )

    transport_emissions = (
        bus_km * bus_factor
        + vehicle_km * vehicle_factor
    )

    waste_emissions = (
        general_waste * general_waste_factor
        + recycled_waste * recycled_waste_factor
    )

    water_emissions = (
        water * water_factor
    )


    # -------------------------------------
    # TOTALS
    # -------------------------------------

    energy_total = (
        electricity_emissions
        + petrol_emissions
        + diesel_emissions
    )

   # -------------------------------------
# VISUAL ANALYSIS
# -------------------------------------

if total_emissions > 0:
    energy_percentage = round((energy_total / total_emissions) * 100, 1)
    transport_percentage = round((transport_emissions / total_emissions) * 100, 1)
    waste_percentage = round((waste_emissions / total_emissions) * 100, 1)
    water_percentage = round((water_emissions / total_emissions) * 100, 1)
else:
    energy_percentage = 0
    transport_percentage = 0
    waste_percentage = 0
    water_percentage = 0

categories = {
    "Energy": energy_total,
    "Transportation": transport_emissions,
    "Waste": waste_emissions,
    "Water": water_emissions
}

highest_category = max(categories, key=categories.get)
highest_value = categories[highest_category]

    # -------------------------------------
    # RESULTS PAGE
    # -------------------------------------

    return render_template(
        "results.html",

        total_emissions=f"{total_emissions:.2f}",

        electricity_emissions=f"{electricity_emissions:.2f}",

        petrol_emissions=f"{petrol_emissions:.2f}",

        diesel_emissions=f"{diesel_emissions:.2f}",

        transport_emissions=f"{transport_emissions:.2f}",

        waste_emissions=f"{waste_emissions:.2f}",

        water_emissions=f"{water_emissions:.2f}",

        energy_total=f"{energy_total:.2f}",
energy_percentage=energy_percentage,
transport_percentage=transport_percentage,
waste_percentage=waste_percentage,
water_percentage=water_percentage,
highest_category=highest_category,
highest_value=f"{highest_value:.2f}"
    )


# =========================================
# CAMPUSCARBON AI - FREE OLLAMA
# =========================================

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    # -------------------------------------
    # GET QUESTION
    # -------------------------------------

    data = request.get_json(silent=True) or {}

    question = str(
        data.get("question", "")
    ).strip()


    if not question:

        return jsonify({
            "answer": "Please type a question first. 🌱"
        }), 400


    # -------------------------------------
    # CAMPUSCARBON AI INSTRUCTIONS
    # -------------------------------------

    instructions = """
You are CampusCarbon AI.

You are the AI sustainability assistant built specifically
for the CampusCarbon college campus carbon footprint
calculator.

Your purpose is to help students, faculty and campus
administrators understand campus carbon emissions and take
practical sustainability actions.

IMPORTANT RULES:

1. Stay focused on campus sustainability and carbon footprints.

2. Explain concepts in simple language suitable for college
   students.

3. You can explain:
   - campus carbon footprint
   - CO2e
   - electricity emissions
   - fuel emissions
   - transportation emissions
   - waste emissions
   - recycling
   - water-related emissions
   - renewable energy
   - energy efficiency
   - sustainable transportation
   - waste reduction
   - practical campus sustainability actions

4. Give practical recommendations that a college campus
   could realistically implement.

5. Do NOT invent campus measurements.

6. Do NOT invent a user's carbon footprint.

7. The actual carbon footprint number is calculated by the
   CampusCarbon Flask calculation engine.

8. AI should explain and interpret calculations, not secretly
   change the calculation.

9. If the user asks something unrelated to campus carbon
   sustainability, politely explain that you are designed
   primarily for CampusCarbon-related questions.

10. Give structured answers when useful.

11. Keep answers SHORT and useful.
    Prefer 2 to 4 short paragraphs or a few bullet points.

12. Be friendly, professional and encouraging.
"""


    # -------------------------------------
    # CREATE PROMPT
    # -------------------------------------

    prompt = f"""
{instructions}

User question:
{question}

Give a short, clear and useful answer.
"""


    # -------------------------------------
    # SEND REQUEST TO OLLAMA
    # -------------------------------------

    try:

        ollama_url = "http://127.0.0.1:11434/api/generate"

        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,

            # Faster and shorter responses
            "options": {
                "num_predict": 100,
                "temperature": 0.3
            }
        }


        request_data = json.dumps(
            payload
        ).encode("utf-8")


        ollama_request = urllib.request.Request(
            ollama_url,
            data=request_data,

            headers={
                "Content-Type": "application/json"
            },

            method="POST"
        )


        with urllib.request.urlopen(
            ollama_request,
            timeout=120
        ) as response:

            response_data = (
                response
                .read()
                .decode("utf-8")
            )


        result = json.loads(
            response_data
        )


        answer = result.get(
            "response",
            ""
        ).strip()


        # -------------------------------------
        # CHECK ANSWER
        # -------------------------------------

        if not answer:

            answer = (
                "I couldn't generate an answer right now. "
                "Please try again. 🌱"
            )


        return jsonify({
            "answer": answer
        })


    # -------------------------------------
    # OLLAMA CONNECTION ERROR
    # -------------------------------------

    except urllib.error.URLError as e:

        print("\n========== OLLAMA ERROR ==========")
        print(str(e))
        print("==================================\n")


        return jsonify({
            "answer": (
                "CampusCarbon AI cannot connect to Ollama. "
                "Please make sure Ollama is running. 🌱"
            )
        }), 500


    # -------------------------------------
    # OTHER ERROR
    # -------------------------------------

    except Exception as e:

        print("\n========== AI ERROR ==========")
        print(str(e))
        print("==============================\n")


        return jsonify({
            "answer": (
                "CampusCarbon AI could not generate an answer "
                "right now. Please try again. 🌱"
            )
        }), 500


# =========================================
# RUN FLASK
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
