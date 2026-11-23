# ai-learning

A simple Python script that sends a question to Google's Gemini model through its API and prints the response, with the API key kept secure.

## Tools
- Python 3.13
- Gemini API (Google AI Studio)
- google-genai
- python-dotenv
- Git & GitHub

## How to run
1. Create and activate a virtual environment:
   `python -m venv venv` then `.\venv\Scripts\Activate.ps1`
2. Install the libraries:
   `pip install google-genai python-dotenv`
3. Create a `.env` file and add your own key:
   `GEMINI_API_KEY=your_key_here`
4. Run the script:
   `python main.py`

## Files
- `main.py`: sends a prompt to the model and prints the reply
- `list_models.py`: lists the models available for your API key

## What I learned
- How to call an AI model (Gemini) from Python using an API
- How to keep API keys secret using a `.env` file and `.gitignore`
- How to connect a local project to GitHub and push it safely
- How to read error messages (4xx = my mistake, 5xx = server issue)