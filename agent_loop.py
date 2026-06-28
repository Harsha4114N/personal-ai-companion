import json
import time
from google import genai
from google.genai import types

# 1. Initialize the modern GenAI Client
# (Ensure your API key is correctly configured)
api_key="YOUR_API_KEY"

print("\n==============================================")
print("🤖 AGENTIC CRITIC-LOOP COGNITIVE ENGINE ONLINE")
print("==============================================\n")

topic = input("Enter a topic, concept, or idea to deconstruct: ")
print(f"\n[System] Spawning research agents for: '{topic}'...")

# Initialize loop variables
passed_evaluation = False
iteration = 1
max_iterations = 3  # Safety cap to prevent infinite loops
current_draft = ""
feedback = "This is the initial run. Generate the first comprehensive deep-dive."

while not passed_evaluation and iteration <= max_iterations:
    print(f"\n🔄 [Iteration {iteration}] Generating/Refining draft based on feedback...")
    
    # --- STAGE 1: THE RESEARCH & COMPOSITION AGENT ---
    researcher_prompt = f"""
    You are an elite researcher and world-class educator. Deconstruct the topic: '{topic}'.
    You must format your response using the following strict sections:

    ## 1. Ground Truth & Deep Explanation
    Provide a clear, profound, and highly scannable explanation of the concept. Avoid superficial summaries.

    ## 2. The Insider Perspective (What the Top 1% Know)
    Reveal insights, mental models, or execution secrets that elite practitioners and top experts in this field know, which a normal person or standard textbook wouldn't tell you.

    ## 3. Alternative & Non-Obvious Perspectives
    Break down how this topic is viewed through at least two completely different paradigms, fields, or mental models (e.g., viewing a technical system through biology, or a psychological concept through game theory).

    ## 4. How to Think About This & Move Forward
    Provide a highly actionable, step-by-step roadmap on how to get started or apply this concept immediately. What is the best practical way to leverage this?

    ## 5. Adjacent Concepts to Explore
    List 3 highly related concepts or deeper sub-topics that the user should explore next to achieve absolute mastery.

    ---
    CRITICAL FEEDBACK FROM EVALUATOR TO IMPLEMENT:
    {feedback}
    """
    
    # Generate the draft
    research_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=researcher_prompt
    )
    current_draft = research_response.text

    print(f"🧐 [Iteration {iteration}] Reviewing draft via Evaluator Agent...")
    
    # --- STAGE 2: THE EVALUATOR & CRITIC AGENT ---
    # We use Structured Outputs (JSON) to force the AI to return a clean score and crisp feedback.
    evaluator_prompt = f"""
    You are a strict, unyielding academic critic and execution referee. Your job is to evaluate the following draft about '{topic}'.
    
    Analyze it based on these criteria:
    1. Is the explanation deeply profound or is it just generic textbook fluff?
    2. Does 'The Insider Perspective' actually contain elite secrets, or is it common knowledge?
    3. Are the alternative perspectives genuinely unique?
    4. Is the roadmap highly practical and immediately actionable?

    You must respond strictly in JSON format with two keys:
    - "score": An integer from 1 to 10.
    - "critique": Detailed feedback explaining exactly what is missing, what is generic, and how the researcher must improve it in the next iteration. If the score is 8 or higher, keep the critique brief.

    Draft to evaluate:
    {current_draft}
    """
    
    eval_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=evaluator_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )
    
    # Parse the evaluation results
    try:
        eval_data = json.loads(eval_response.text)
        score = eval_data.get("score", 0)
        feedback = eval_data.get("critique", "No feedback provided.")
    except Exception as e:
        # Fallback if JSON parsing fails
        score = 7
        feedback = "Ensure the content is deeper, less generic, and includes sharper insider secrets."

    print(f"📊 Evaluator Quality Score: {score}/10")
    
    if score >= 8:
        print("✅ Quality threshold met! Finalizing report...")
        passed_evaluation = True
    else:
        print(f"❌ Improvement Required. Critic Feedback: {feedback}")
        iteration += 1
        time.sleep(1) # Polite pause between API cycles

print("\n==========================================================================================")
print("🎯 FINAL EVALUATOR-APPROVED REPORT")
print("==========================================================================================\n")
print(current_draft)
print("\n==========================================================================================")