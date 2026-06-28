import google.generativeai as genai
from gtts import gTTS
import os

# 1. Setup the AI Brain
# Replace 'YOUR_API_KEY' with the key you got from Google AI Studio
api_key="YOUR_API_KEY"
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. The User Input
user_topic = input("What do you want the AI to explain? (e.g., U-Net architectures): ")
prompt = f"Write a detailed, comprehensive four-paragraph essay explaining {user_topic} in depth."

print(f"\nThinking about {user_topic}...")
    
# 3. Call API #1 (Text Generation)
response = model.generate_content(prompt)
ai_script = response.text
print(f"\nThe Script:\n{ai_script}\n")

# 4. Call API #2 (Audio Generation)
print("Converting text to audio...")
tts = gTTS(text=ai_script, lang='en', slow=False)

# 5. Save the output
output_file = "explanation.mp3"
tts.save(output_file)
print(f"Done! Audio saved as {output_file}")

# Optional: Automatically play the file (Windows/Mac/Linux)
os.system(f"start {output_file}" if os.name == 'nt' else f"open {output_file}")