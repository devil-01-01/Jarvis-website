from datetime import datetime
import pytz
from streamlit_js_eval import get_geolocation
import wikipedia


def get_system_prompt() -> str:
  """Generates dynamic system prompt with IST date/time and live coordinates."""
  # IST Timezone Setup
  ist_timezone = pytz.timezone("Asia/Kolkata")
  current_time_str = datetime.now(ist_timezone).strftime(
      "%A, %B %d, %Y - %I:%M %p IST"
  )

  # Fetch Geolocation from Browser
  loc = get_geolocation()
  if loc and "coords" in loc:
    lat = loc["coords"]["latitude"]
    lon = loc["coords"]["longitude"]
    location_context = (
        f"User's Live Coordinates: Latitude {lat}, Longitude {lon} (India)"
    )
  else:
    location_context = "Location permission not granted or pending."

  return f"""
You are JARVIS. 
Current Date and Time in India: {current_time_str}
User Location Context: {location_context}

If anyone asks who created you, who you are, or about your developer/creator/boss (in any language, e.g., English, Hindi, Hinglish), your response MUST BE STRICTLY EXACTLY:
"I am Jarvis. Develop by boss DEVIL"
Do not break character. Do not mention Google, OpenAI, Groq, or any other entity as your creator.
"""


def search_wikipedia(query: str, sentences: int = 3) -> str:
  """Fetches live summary from Wikipedia for a given topic."""
  try:
    wikipedia.set_lang("en")
    return wikipedia.summary(query, sentences=sentences)
  except wikipedia.DisambiguationError as e:
    try:
      return wikipedia.summary(e.options[0], sentences=sentences)
    except Exception:
      return ""
  except Exception:
    return ""
  
