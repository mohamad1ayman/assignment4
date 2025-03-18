# assignment4
# Conversational Assistant with Weather and Calculator Tools

## Overview
This project is a Python-based conversational assistant that provides weather information, performs mathematical calculations, and simulates web searches. It utilizes APIs for real-time weather data and provides reasoning-based responses.

## Features
- Fetch current weather data for a specified location
- Retrieve weather forecasts for upcoming days
- Perform mathematical calculations
- Simulate web searches for general knowledge

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package manager)

### Step 1: Clone the Repository
```sh
git clone https://github.com/mohamad1ayman/assignment4.git
cd assignment4
```

### Step 2: Install Dependencies
Install the required Python packages by running:
```sh
pip install -r requirements.txt
```
Ensure `requirements.txt` contains:
```
requests
dotenv
openai
```

### Step 3: Set Up Environment Variables
Create a `.env` file in the project directory and add the following:
```
API_KEY=your_openai_api_key
WEATHER_API_KEY=your_weather_api_key
BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```
Replace `your_openai_api_key` and `your_weather_api_key` with valid API keys.

### Step 4: Run the Application
Execute the script to test functionality:
```sh
python conversational_agent.py
```

## Usage
You can call functions within the script:
```python
print(get_current_weather("New York"))
print(get_weather_forecast("London", days=5))
print(calculator("5 + 3 * 2"))
print(web_search("climate change"))
```

## License
This project is for educational purposes only.

