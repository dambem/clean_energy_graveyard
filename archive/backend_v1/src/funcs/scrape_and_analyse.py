import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import os
import io
load_dotenv()
api_key= os.getenv("GEMINI_API_KEY")

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
  "temperature": 1.5,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
from markitdown import MarkItDown


def scrape_content(url, mime="none", max_chars=10000):
    try:
        if url.lower().endswith('.pdf') or mime=='application/pdf':
            response = requests.get(url, timeout=10)
            md = MarkItDown(enable_plugins=False) # Set to True to enable plugins
            pdf = io.BytesIO(response.content)
            result = md.convert(pdf)
            result = result[0:max_chars]
            print(result)
            return result

        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser")
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        content_pieces = []

            
        main_content = soup.find(['main', 'article', 'div.content', 'div#content'])
        if main_content:
            paragraphs = main_content.find_all("p")
            content_pieces.append(" ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)))

        if len(content_pieces) == 0:
            paragraphs = soup.find_all("p")
            content_pieces.append(" ".join(p.get_text() for p in paragraphs))

        if len(content_pieces) == 0:
            body = soup.find('body')
            if body:
                full_content = body.get_text(strip=True, separator=' ')

        # print(content_pieces)
        if content_pieces == ['']:
            content_pieces.append(['Struggled to parse'])
            
        full_content = " ".join(content_pieces).strip()
        if max_chars and len(full_content) > max_chars:
            full_content = full_content[:max_chars] + "..."

        return full_content
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occured when scraping {url}: {e}")
        return None

def load_prompt(filepath):
    """Loads the prompt from a text file."""
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {filepath}")
        return None  # Or raise the exception, depending on desired behavior


def load_json(filepath):
    """Loads the prompt from a text file."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            pass
def gemini_process(content, prompt="data/nimby_prompt.txt"):
    prompt_filepath = "data/nimby_prompt.txt"  # Adjust the path if needed
    nimby_radar_prompt = load_prompt(prompt_filepath)
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )
    
    chat_session = model.start_chat(
    history=[      {
            "role": "user",  # or "model" if it was a prior model response
            "parts": [nimby_radar_prompt]
        }])
    if len(content) > 0:
        response = chat_session.send_message(content).text
    else:
        response = load_prompt("data/backup_object.json")
    return response

def parse_json_string(json_string):
    cleaned_string = json_string.replace("```json", "").replace("```", "")
    cleaned_string = cleaned_string.replace("\\n", "\n")
    try:
        json_object = json.loads(cleaned_string)
        return json_object
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {str(e)}"

# def parse_date():
    

def convert_points_geojson():
    geo_json = ""
    with open("points.geojson", 'r', encoding="utf-8") as f:
        try:
            geo_json =  json.load(f)
        except FileNotFoundError:
            return "Error parsing Geojson"
    print(geo_json)

# content = scrape_content('https://www.hampshirechronicle.co.uk/news/20076213.controversial-solar-farm-plan-godsfield-near-alresford-withdrawn-developers/')
# ai = gemini_process(content)

# with open('nimby_score.json', "w", encoding="utf-8") as f:
#     json.dump(parse_json_string(ai.text), f, ensure_ascii=False, indent=4)
    
# print(ai.text)