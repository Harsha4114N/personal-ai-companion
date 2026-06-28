from google import genai

# 1. Setup the modern GenAI Client
# (Make sure to replace with your actual API key)
api_key="YOUR_API_KEY"

# 2. The User Input
print("\n--- THE MASTER EXPLAINER ---")
user_topic = input("Enter a concept you want to master (e.g., U-Net architectures): ")
print(f"\nAnalyzing and structuring the best learning path for: {user_topic}...\n")

# 3. The Master Blueprint Prompt
prompt = f"""
You are an elite, world-class educator. Explain the concept of '{user_topic}' using the following strict structure. Do not deviate from this format.

## 1. The Brief (Beginner Level)
Provide a dead-simple, two-sentence explanation that a complete beginner could understand.

## 2. The Master Structure (Intermediate to Mastery)
Explain the core mechanics deeply. Choose the absolute best teaching framework for this specific topic (e.g., the Feynman technique, a mechanical analogy, or a step-by-step breakdown). Clearly state which teaching style you are using, and then deliver the explanation.

## 3. Different Perspectives
Explain how this concept is viewed or utilized across two completely different fields, professions, or paradigms.

## 4. The Next Step (Related Concepts)
List exactly 3 related concepts or real-world applications that logically follow this topic. Provide a one-sentence summary for each so the user knows what to study next.
"""

# 4. Generate the Response
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)

# 5. Print the Output
print("==================================================")
print(response.text)
print("==================================================")