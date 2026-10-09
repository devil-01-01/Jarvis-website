from datetime import datetime
import pytz
import streamlit.components.v1 as components
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


def render_chat_action_toolbar():
  """Renders Gemini-style action buttons (Plus, Mic, Live audio) with browser permission handling."""
  toolbar_html = """
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 5px; padding: 4px;">
        <button title="Add Attachment" onclick="alert('Attachment feature clicked!')" style="background: transparent; border: 1px solid #ccc; border-radius: 50%; width: 36px; height: 36px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 18px;">➕</button>
        <button title="Voice Input" onclick="startSpeechRec()" style="background: transparent; border: 1px solid #ccc; border-radius: 50%; width: 36px; height: 36px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 16px;">🎙️</button>
        <button title="Live Mode" onclick="alert('Live voice mode starting...')" style="background: #e8f0fe; border: none; border-radius: 20px; padding: 6px 14px; cursor: pointer; display: flex; align-items: center; gap: 6px; font-weight: 500; color: #1a73e8; font-size: 14px;">🔊 Live</button>
    </div>
    <script>
    function startSpeechRec() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            var recognition = new SpeechRecognition();
            recognition.lang = "hi-IN";
            recognition.start();
            
            recognition.onresult = function(e) {
                var transcript = e.results[0][0].transcript;
                navigator.clipboard.writeText(transcript);
                alert("Recognized & Copied to clipboard: " + transcript);
            };
            
            recognition.onerror = function(e) {
                if(e.error === 'not-allowed') {
                    alert("Microphone permission denied! Please allow mic access in your browser settings.");
                } else {
                    alert("Speech error: " + e.error);
                }
            };
        } else {
            alert("Speech recognition is not supported in this browser.");
        }
    }
    </script>
    """
  return components.html(toolbar_html, height=50)
    
