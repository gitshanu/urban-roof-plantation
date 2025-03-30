# Urban Roof Plantation

Urban Roof Plantation is a web application designed to recommend crops for rooftop gardening and provide AI-powered gardening assistance. Built with Flask, pandas, and Together AI, it processes user inputs (area, water, sunlight) to suggest suitable crops and offers a chatbot for real-time queries. Deployed on Render, this project promotes sustainable urban living.

Live Demo: [https://urban-roof-plantation.onrender.com](https://urban-roof-plantation.onrender.com)

## Features
- **Crop Recommendation**: Enter rooftop area, water capacity, and sunlight hours to get a list of suitable crops.
- **AI Chatbot**: Ask gardening questions (e.g., "How much water for tomatoes?") and get instant answers.
- **Responsive UI**: Simple, user-friendly interface built with HTML, CSS, and JavaScript.

## Tech Stack
- **Backend**: Flask (Python), pandas (data processing)
- **AI**: Together AI (NLP chatbot)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render (with Gunicorn)
- **Version Control**: Git

## Project Structure
urban-roof-plantation/
├── static/           # CSS, JS, and images (e.g., leaf.png)
├── templates/        # HTML files (index.html, result.html)
├── app.py            # Main Flask application
├── crop_data.csv     # Crop dataset
├── requirements.txt  # Python dependencies


## How It Works
1. **Crop Recommendation**:
   - User inputs area, water, and sunlight via a form.
   - `recommend_crops()` filters `crop_data.csv` using pandas.
   - Returns a table of matching crops or an error message.
2. **AI Chatbot**:
   - User types a query in the chat widget.
   - `/chat` route sends it to Together AI’s Llama-3 model.
   - Displays the AI’s response in real-time.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/gitshanu/urban-roof-plantation.git
   cd urban-roof-plantation

Install Dependencies:
   pip install -r requirements.txt

   Set Environment Variable
export TOGETHER_AI_API_KEY="your_api_key_here"

Run Locally
python app.py
