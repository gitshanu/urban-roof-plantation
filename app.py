import pandas as pd
from flask import Flask, request, render_template, jsonify
from together import Together

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(BASE_DIR, "crop_data.csv"))

together_client = Together(api_key=os.environ.get("c3d2c0fb6d80cded08f811ae119f4a22106fcc8fd31beadbd6ea143fda765465"))

def recommend_crops(rooftop_area, water_capacity, sunlight_hours):
    if rooftop_area <= 0 or water_capacity <= 0 or sunlight_hours <= 0:
        return pd.DataFrame(), "Inputs must be positive numbers."
    
    viable_crops = data[data["Sunlight Hours (per day)"] <= sunlight_hours].copy()
    if viable_crops.empty:
        return pd.DataFrame(), f"No crops in our dataset can grow with only {sunlight_hours} hours of sunlight."
    
    viable_crops["Max Pots (Water)"] = (water_capacity / viable_crops["Water Requirement (L/day)"]).astype(int)
    viable_crops["Max Pots (Area)"] = (rooftop_area / (viable_crops["Pot Spacing (cm)"] ** 2)).astype(int)
    viable_crops["Max Pots"] = viable_crops[["Max Pots (Water)", "Max Pots (Area)"]].min(axis=1)
    viable_crops["Water Per Plant (L/day)"] = viable_crops["Water Requirement (L/day)"]
    viable_crops["Total Water Needed (L/day)"] = viable_crops["Water Requirement (L/day)"] * viable_crops["Max Pots"]
    viable_crops = viable_crops[viable_crops["Max Pots"] > 0]
    
    if viable_crops.empty:
        return pd.DataFrame(), f"Your water ({water_capacity} L) or area ({rooftop_area/10000} m²) is too limited for any crops with {sunlight_hours} hours of sunlight."
    
    recommendations = viable_crops[["Crop Name", "Soil Type", "Pot Spacing (cm)", 
                                   "Irrigation Technique", "Fertilizer Type", "Max Pots", 
                                   "Water Per Plant (L/day)", "Total Water Needed (L/day)"]]
    return recommendations, None

last_inputs = {"area": None, "water": None, "sunlight": None}

@app.route("/", methods=["GET", "POST"])
def home():
    global last_inputs
    if request.method == "POST":
        try:
            area = float(request.form["area"]) * 10000
            water = float(request.form["water"])
            sunlight = float(request.form["sunlight"])
            last_inputs = {"area": area, "water": water, "sunlight": sunlight}
            
            result, message = recommend_crops(area, water, sunlight)
            if not result.empty:
                return render_template("result.html", tables=[result.to_html(index=False, classes="table")])
            else:
                return render_template("result.html", message=message or "No suitable crops found.")
        except ValueError:
            return render_template("result.html", message="Please enter valid numbers for area, water, and sunlight.")
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message").lower().strip()

    if "hi" in user_message or "hello" in user_message:
        return jsonify({"response": "Hi! I’m your Urban Roof Plantation Assistant. I can help with crop details, fertilizer info, or your rooftop setup. What’s your question?"})

    crop_name = next((word.capitalize() for word in user_message.split() if word.capitalize() in data["Crop Name"].values), None)
    if crop_name:
        crop_data = data[data["Crop Name"] == crop_name].iloc[0]
        if "water" in user_message and "need" in user_message:
            return jsonify({"response": f"{crop_name} requires {crop_data['Water Requirement (L/day)']} L of water per plant per day."})
        elif "soil" in user_message:
            return jsonify({"response": f"For {crop_name}, use {crop_data['Soil Type']} soil for optimal growth."})
        elif "fertilizer" in user_message or "npk" in user_message:
            return jsonify({"response": f"{crop_name} benefits from {crop_data['Fertilizer Type']} fertilizer."})
        elif "sunlight" in user_message:
            return jsonify({"response": f"{crop_name} needs {crop_data['Sunlight Hours (per day)']} hours of sunlight daily."})
        elif "how many" in user_message and "pots" in user_message and last_inputs["sunlight"] is not None:
            result, _ = recommend_crops(last_inputs["area"], last_inputs["water"], last_inputs["sunlight"])
            if not result.empty and crop_name in result["Crop Name"].values:
                pots = result[result["Crop Name"] == crop_name]["Max Pots"].iloc[0]
                total_water = result[result["Crop Name"] == crop_name]["Total Water Needed (L/day)"].iloc[0]
                return jsonify({"response": f"Based on your inputs (area: {last_inputs['area']/10000} m², water: {last_inputs['water']} L, sunlight: {last_inputs['sunlight']} hrs), you can grow {pots} pots of {crop_name}, needing {total_water:.1f} L/day total."})
            else:
                return jsonify({"response": f"{crop_name} isn’t viable with your last inputs—adjust area, water, or sunlight."})
        elif "grow" in user_message or "tips" in user_message:
            return jsonify({"response": f"To grow {crop_name}, use {crop_data['Soil Type']} soil, provide {crop_data['Water Requirement (L/day)']} L/day per plant, ensure {crop_data['Sunlight Hours (per day)']} hours of sunlight, and apply {crop_data['Fertilizer Type']} fertilizer."})
        else:
            return jsonify({"response": f"{crop_name} specifics: {crop_data['Water Requirement (L/day)']} L/day per plant, {crop_data['Sunlight Hours (per day)']} hours sunlight, {crop_data['Soil Type']} soil, {crop_data['Fertilizer Type']} fertilizer."})

    if "10-10-10" in user_message and ("npk" in user_message or "fertilizer" in user_message):
        crops_using = data[data["Fertilizer Type"] == "10-10-10 NPK"]["Crop Name"].tolist()
        return jsonify({"response": f"10-10-10 NPK is a balanced fertilizer (10% nitrogen, 10% phosphorus, 10% potassium) for overall plant health. In your rooftop garden, it’s used by: {', '.join(crops_using)}."})
    elif "20-20-20" in user_message and ("npk" in user_message or "fertilizer" in user_message):
        crops_using = data[data["Fertilizer Type"] == "20-20-20 NPK"]["Crop Name"].tolist()
        return jsonify({"response": f"20-20-20 NPK is a potent balanced mix (20% nitrogen, phosphorus, potassium) for strong growth. It’s used by: {', '.join(crops_using)}."})
    elif "npk" in user_message:
        return jsonify({"response": "NPK means nitrogen (N), phosphorus (P), and potassium (K)—vital for plants. Nitrogen boosts leaves, phosphorus strengthens roots, and potassium enhances resilience. Ask about a specific NPK like 10-10-10!"})

    if "why no crops" in user_message and last_inputs["sunlight"] is not None:
        result, message = recommend_crops(last_inputs["area"], last_inputs["water"], last_inputs["sunlight"])
        return jsonify({"response": message or f"Your inputs (area: {last_inputs['area']/10000} m², water: {last_inputs['water']} L, sunlight: {last_inputs['sunlight']} hrs) support crops—see the recommendations!"})
    elif "best crop" in user_message and last_inputs["sunlight"] is not None:
        result, _ = recommend_crops(last_inputs["area"], last_inputs["water"], last_inputs["sunlight"])
        if not result.empty:
            best_crop = result.iloc[0]["Crop Name"]
            pots = result.iloc[0]["Max Pots"]
            return jsonify({"response": f"With your inputs (area: {last_inputs['area']/10000} m², water: {last_inputs['water']} L, sunlight: {last_inputs['sunlight']} hrs), {best_crop} is ideal—you can grow {pots} pots."})
        else:
            return jsonify({"response": "No crops match your last inputs. Try increasing water or sunlight!"})
    elif "my inputs" in user_message and last_inputs["sunlight"] is not None:
        return jsonify({"response": f"Your last inputs were: area = {last_inputs['area']/10000} m², water = {last_inputs['water']} L, sunlight = {last_inputs['sunlight']} hours."})

    if "help" in user_message:
        return jsonify({"response": "I’m here for your rooftop garden! Ask specifics like 'Tomato water needs,' '10-10-10 NPK,' 'best crop,' or 'why no crops?'—what do you want to know?"})

    system_prompt = (
        "You are a rooftop gardening expert for the Urban Roof Plantation project. "
        "Answer questions precisely about crops, fertilizers, irrigation, or gardening inputs. "
        "Stick to facts, avoid speculation, and keep it concise. If unsure, suggest a related gardening topic."
    )
    response = together_client.chat.completions.create(
        model="meta-llama/Llama-3-8b-chat-hf",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=120,
        temperature=0.5,
        top_p=0.9
    )
    answer = response.choices[0].message.content.strip()
    if not answer or len(answer) < 10:
        answer = "I’m not sure about that—try asking about a crop, fertilizer, or your garden inputs!"
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)