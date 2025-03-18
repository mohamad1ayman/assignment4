import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def get_current_weather(location):
    """Fetch current weather for a given location."""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={location}&aqi=no"
    response = requests.get(url)
    data = response.json()
    
    if "error" in data:
        return f"Error: {data['error']['message']}"
    
    return json.dumps({
        "location": data["location"]["name"],
        "temperature_c": data["current"]["temp_c"],
        "temperature_f": data["current"]["temp_f"],
        "condition": data["current"]["condition"]["text"],
        "humidity": data["current"]["humidity"],
        "wind_kph": data["current"]["wind_kph"]
    })

def get_weather_forecast(location, days=3):
    """Fetch a weather forecast for a given location."""
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days={days}&aqi=no"
    response = requests.get(url)
    data = response.json()
    
    if "error" in data:
        return f"Error: {data['error']['message']}"

    forecast_data = [
        {
            "date": day["date"],
            "max_temp_c": day["day"]["maxtemp_c"],
            "min_temp_c": day["day"]["mintemp_c"],
            "condition": day["day"]["condition"]["text"],
            "chance_of_rain": day["day"]["daily_chance_of_rain"]
        }
        for day in data["forecast"]["forecastday"]
    ]

    return json.dumps({
        "location": data["location"]["name"],
        "forecast": forecast_data
    })

# Task 2.1: Create a Calculator Tool
def calculator(expression):
    """
    Evaluate a mathematical expression.
    Args:
        expression: A mathematical expression as a string
    Returns:
        The result of the evaluation
    """
    try:
        # Safely evaluate the expression
        # Note: This is not completely safe for production use
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Task 2.2: Define the Calculator Tool
calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g., '2 + 2' or '5 * (3 + 2)'",
                }
            },
            "required": ["expression"],
        },
    }
}

# Task 3.1: Create a Search Tool
def web_search(query):
    """
    Simulate a web search for information.
    Args:
        query: The search query
    Returns:
        Search results as JSON
    """
    # This is a simulated search function
    # In a real application, you would use an actual search API
    search_results = {
        "weather forecast": "Weather forecasts predict atmospheric conditions for a specific location and time period. They typically include temperature, precipitation, wind, and other variables.",
        "temperature conversion": "To convert Celsius to Fahrenheit: multiply by 9/5 and add 32. To convert Fahrenheit to Celsius: subtract 32 and multiply by 5/9.",
        "climate change": "Climate change refers to significant changes in global temperature, precipitation, wind patterns, and other measures of climate that occur over several decades or longer.",
        "severe weather": "Severe weather includes thunderstorms, tornadoes, hurricanes, blizzards, floods, and high winds that can cause damage, disruption, and loss of life."
    }

    # Find the closest matching key
    best_match = None
    best_match_score = 0
    for key in search_results:
        # Simple matching algorithm
        words_in_query = set(query.lower().split())
        words_in_key = set(key.lower().split())
        match_score = len(words_in_query.intersection(words_in_key))
        if match_score > best_match_score:
            best_match = key
            best_match_score = match_score

    if best_match_score > 0:
        return json.dumps({"query": query, "result": search_results[best_match]})
    else:
        return json.dumps({"query": query, "result": "No relevant information found."})

# Task 3.2: Define the Search Tool
search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search for information on the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
            "required": ["query"],
        },
    }
}

# Define tool sets
weather_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get the weather forecast for a given location",
            "parameters": {"type": "object", "properties": {"location": {"type": "string"}, "days": {"type": "integer"}}, "required": ["location"]}
        },
    }
]

# Create tool sets for different reasoning patterns
cot_tools = weather_tools + [calculator_tool]
react_tools = cot_tools + [search_tool]

# Available functions dictionary
available_functions = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
    "calculator": calculator,
    "web_search": web_search
}

# Task 2.3: Create a Chain of Thought Prompt
cot_system_message = """You are a helpful assistant that can answer questions about weather and perform calculations.
When responding to complex questions, please follow these steps:
1. Think step-by-step about what information you need
2. Break down the problem into smaller parts
3. Use the appropriate tools to gather information
4. Explain your reasoning clearly
5. Provide a clear final answer

For example, if someone asks about temperature conversions or comparisons between cities, first get the weather data, then use the calculator if needed, showing your work.
"""

# Task 3.3: Create a ReAct Prompt
react_system_message = """You are a helpful weather and information assistant that uses the ReAct (Reasoning and Acting) approach to solve problems.

When responding to questions, follow this pattern:
1. Thought: Think about what you need to know and what steps to take
2. Action: Use a tool to gather information (weather data, search, calculator)
3. Observation: Review what you learned from the tool
4. ... (repeat the Thought, Action, Observation steps as needed)
5. Final Answer: Provide your response based on all observations

For example:
User: What's the temperature difference between New York and London today?
Thought: I need to find the current temperatures in both New York and London, then calculate the difference.
Action: [Use get_current_weather for New York]
Observation: [Results from weather tool]
Thought: Now I need London's temperature.
Action: [Use get_current_weather for London]
Observation: [Results from weather tool]
Thought: Now I can calculate the difference.
Action: [Use calculator to subtract]
Observation: [Result of calculation]
Final Answer: The temperature difference between New York and London today is X degrees.

Always make your reasoning explicit and show your work.
"""

def process_messages(client, messages, tools=None, available_functions=None):
    """
    Process messages and invoke tools as needed.
    """
    # If tools and available_functions are None, use empty list/dict
    tools = tools or []
    available_functions = available_functions or {}
    
    # Print for debugging
    print("Sending message to model...")
    
    try:
        # Send the messages to the model with the tool definitions
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"  # Add explicit tool_choice
        )
        
        # Extract the assistant's message
        response_message = response.choices[0].message
        
        # Add the response message to our conversation
        messages.append({"role": "assistant", "content": response_message.content, "tool_calls": response_message.tool_calls})
        
        # Handle tool calls if any
        if response_message.tool_calls:
            print(f"Tool calls detected: {len(response_message.tool_calls)}")
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Calling function: {function_name} with args: {function_args}")
                
                # Call the function
                function_to_call = available_functions[function_name]
                function_response = function_to_call(**function_args)
                
                # Add the function response to our conversation
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })
            
            # After adding all tool responses, make a second API call to get final response
            print("Getting final response after tool calls...")
            second_response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages
            )
            
            # Add the final response to our conversation
            final_message = second_response.choices[0].message
            messages.append({"role": "assistant", "content": final_message.content})
        
        return messages
    
    except Exception as e:
        print(f"Error in API call: {e}")
        messages.append({"role": "assistant", "content": f"I'm sorry, I encountered an error: {str(e)}"})
        return messages

def run_conversation(client, system_message="You are a helpful weather assistant.", tools=None):
    """
    Run a conversation with the user, processing their messages and handling tool calls.
    """
    messages = [
        {
            "role": "system",
            "content": system_message,
        }
    ]
    
    print("Weather Assistant: Hello! I can help you with weather information. Ask me about the weather anywhere!")
    print("(Type 'exit' to end the conversation)\n")
    
    while True:
        try:
            # Request user input and append to messages
            user_input = input("You: ")
            if not user_input.strip():  # Check for empty input
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nWeather Assistant: Goodbye! Have a great day!")
                break
                
            messages.append({
                "role": "user",
                "content": user_input,
            })
            
            # Process the messages and handle tool calls
            before_len = len(messages)
            messages = process_messages(client, messages, tools, available_functions)
            
            # Print all new messages from the assistant
            for i in range(before_len, len(messages)):
                if messages[i]["role"] == "assistant" and messages[i].get("content"):
                    print(f"\nWeather Assistant: {messages[i]['content']}\n")
                elif messages[i]["role"] == "tool":
                    tool_content = messages[i].get("content", "")
                    try:
                        # Try to parse JSON for better display
                        parsed = json.loads(tool_content)
                        print(f"\n[Tool Response - {messages[i]['name']}]: {json.dumps(parsed, indent=2)}\n")
                    except:
                        print(f"\n[Tool Response - {messages[i]['name']}]: {tool_content}\n")
            
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            continue
            
    return messages

# Bonus Challenge: Comparative Evaluation System
def comparative_evaluation(client, query):
    """
    Processes a single query with all three agent types and compares their responses.
    """
    # Define the agents
    agents = [
        {"name": "Basic", "system_message": "You are a helpful weather assistant.", "tools": weather_tools},
        {"name": "Chain of Thought", "system_message": cot_system_message, "tools": cot_tools},
        {"name": "ReAct", "system_message": react_system_message, "tools": react_tools}
    ]
    
    # Process the query with each agent
    responses = []
    for agent in agents:
        print(f"\nProcessing with {agent['name']} agent...\n")
        messages = [
            {"role": "system", "content": agent["system_message"]},
            {"role": "user", "content": query}
        ]
        
        try:
            processed_messages = process_messages(client, messages, agent["tools"], available_functions)
            
            # Get the final assistant's response
            assistant_responses = [msg for msg in processed_messages if msg["role"] == "assistant" and msg.get("content")]
            if assistant_responses:
                # Get the last assistant response
                last_response = assistant_responses[-1]["content"]
                responses.append({"agent": agent["name"], "response": last_response})
                print(f"\n{agent['name']} response: {last_response}\n")
            else:
                responses.append({"agent": agent["name"], "response": "No response generated"})
                print(f"\n{agent['name']}: No response generated\n")
                
        except Exception as e:
            print(f"Error with {agent['name']} agent: {str(e)}")
            responses.append({"agent": agent["name"], "response": f"Error: {str(e)}"})
    
    # Display the responses side by side
    print("\n" + "="*60)
    print("Comparative Results:")
    print("="*60)
    
    for response in responses:
        print(f"\n{response['agent']} Agent:\n{response['response']}\n")
        print("-"*60)
    
    # Ask the user to rate each response
    ratings = []
    print("\nPlease rate each response on a scale of 1-5 (1=Poor, 5=Excellent):")
    for response in responses:
        try:
            rating = int(input(f"{response['agent']} Agent rating (1-5): "))
            if 1 <= rating <= 5:
                ratings.append({"agent": response["agent"], "rating": rating})
            else:
                print("Invalid rating. Please enter a number between 1 and 5.")
                ratings.append({"agent": response["agent"], "rating": None})
        except ValueError:
            print("Invalid input. Please enter a number.")
            ratings.append({"agent": response["agent"], "rating": None})
    
    # Save the results to a CSV file
    try:
        import csv
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_comparison_{timestamp}.csv"
        
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["query", "agent", "response", "rating"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for i, response in enumerate(responses):
                writer.writerow({
                    "query": query,
                    "agent": response["agent"],
                    "response": response["response"],
                    "rating": ratings[i]["rating"] if i < len(ratings) else None
                })
        
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving CSV: {str(e)}")
    
    return responses, ratings

if __name__ == "__main__":
    choice = input("Choose an option:\n1: Basic Weather Assistant\n2: Chain of Thought Agent\n3: ReAct Agent\n4: Comparative Evaluation\nYour choice: ")
    
    if choice == "1":
        system_message = "You are a helpful weather assistant."
        tools = weather_tools
        run_conversation(client, system_message, tools)
    elif choice == "2":
        system_message = cot_system_message
        tools = cot_tools
        run_conversation(client, system_message, tools)
    elif choice == "3":
        system_message = react_system_message
        tools = react_tools
        run_conversation(client, system_message, tools)
    elif choice == "4":
        query = input("\nEnter a query to compare all three agents: ")
        comparative_evaluation(client, query)
    else:
        print("Invalid choice. Defaulting to Basic agent.")
        system_message = "You are a helpful weather assistant."
        tools = weather_tools
        run_conversation(client, system_message, tools)