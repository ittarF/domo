import requests
import json
from dotenv import load_dotenv
import os

def get_openrouter_response(prompt: str, model: str = "openrouter/quasar-alpha", max_tokens: int = 500, temperature: float = 0.7) -> str:
    """
    Sends a prompt to a specified model via OpenRouter API and returns the response.
    
    Args:
        prompt (str): The input prompt to send to the model.
        model (str): The model to use (default: 'xai/quasar-alpha-1m').
        max_tokens (int): Maximum number of tokens in the response (default: 500).
        temperature (float): Controls response creativity, 0.0 to 1.0 (default: 0.7).
    
    Returns:
        str: The model's response text.
    
    Raises:
        ValueError: If prompt or model is empty/invalid.
        Exception: If the API request fails or returns an error.
    """
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found in .env file. Set OPENROUTER_API_KEY.")
    if not prompt or not isinstance(prompt, str):
        raise ValueError("Prompt must be a non-empty string.")
    if not model or not isinstance(model, str):
        raise ValueError("Model must be a non-empty string.")

    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Headers for authentication and request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  # Optional: Your app's URL
        "X-Title": "OpenRouter Client"       # Optional: Your app's name
    }
    
    # Payload with the specified model and prompt
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    try:
        # Send POST request to OpenRouter
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the JSON response
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except (KeyError, IndexError) as e:
        raise Exception(f"Error parsing response: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        # Example prompt and model
        prompt = "are you suitable to power ai agents and execute a list of given tools etc?"
        response = get_openrouter_response(prompt, model="openrouter/quasar-alpha")
        print("Model Response:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")