# ai-learning

A hands-on project where I learn to build AI-powered tools step by step: from a first API call to a customer-message classifier, then a full automation in n8n.

## Projects

### 1. First Gemini API call (`main.py`)
A Python script that sends a question to Google's Gemini model and prints the response, with the API key kept secure in a `.env` file.

### 2. Customer message classifier (`day2_json.py`)
Classifies e-commerce customer messages into **inquiry / complaint / request / other** and sets a **priority**, returning structured JSON.

- Uses a JSON schema with fixed allowed values, so the model cannot invent new categories
- Temperature set to 0 for consistent results
- Includes a test set of 8 messages with expected answers, and calculates accuracy
- Retries automatically when the server is busy (503) and waits between requests to respect rate limits
- **Result: 8/8 correct** on `gemini-3.7-flash` and `gemini-3.1-flash-lite` (see `results.csv`)

### 3. n8n automation (`n8n/`)
The same classifier as a no-code automation:

`Trigger → Customer message → Gemini (classify) → Prepare data → Save to table`

- Gemini node with system instructions, JSON output, temperature 0, and automatic retry
- Parses the model's JSON response and saves message, category and priority to an n8n data table
- **Result: 3/3 test messages classified correctly**

![n8n workflow](n8n/workflow_success.png)

## Tools
- Python 3.13
- Gemini API (Google AI Studio)
- google-genai, python-dotenv
- n8n (self-hosted, Node.js 24)
- Git & GitHub

## How to run (Python)
1. Create and activate a virtual environment:
   `python -m venv venv` then `.\venv\Scripts\Activate.ps1`
2. Install the libraries:
   `pip install google-genai python-dotenv`
3. Create a `.env` file and add your own key:
   `GEMINI_API_KEY=your_key_here`
4. Run a script, for example:
   `python day2_json.py`

## How to use the n8n workflow
1. Install n8n: `npm install -g n8n`, then run `n8n start`
2. Open `http://localhost:5678` and import `n8n/customer_message_classifier.json`
3. Add your own Gemini API key as a credential in n8n

## Files
- `main.py`: first call to the model
- `list_models.py`: lists the models available for your API key
- `day2_tokens.py`: token counting and temperature experiments
- `day2_prompt.py`: classification with system instructions
- `day2_json.py`: classifier with JSON schema, test set and accuracy
- `results.csv`: latest test results
- `n8n/`: exported n8n workflow and screenshots

## What I learned
- How to call an AI model (Gemini) from Python using an API
- How to keep API keys secret using a `.env` file and `.gitignore`
- How to connect a local project to GitHub and push it safely
- How to read error messages (4xx = my mistake, 5xx = server issue)
- How to list the available models for my API key and choose the right one
- Clear instructions turn a long chat answer into a short, usable result
- One clear rule works better than a long page of vague instructions
- Changing one rule can break results that seemed unrelated, so I re-run the full test after every change
- Low temperature plus clear rules gives consistent classification
- How to build an automation in n8n and pass JSON data between steps