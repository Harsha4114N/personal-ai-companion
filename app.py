import streamlit as st
from google import genai
from google.genai import types
import json
import os
import time

# --- CONSTANTS & DATA STORAGE SETUP ---
PROFILE_DB = "user_profiles.json"

def load_profiles():
    if os.path.exists(PROFILE_DB):
        try:
            with open(PROFILE_DB, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_profiles(profiles):
    with open(PROFILE_DB, "w") as f:
        json.dump(profiles, f, indent=4)

# Load existing database profiles
profiles = load_profiles()

# --- MOBILE PAGE STYLING ---
st.set_page_config(page_title="Personal AI OS", page_icon="🧠", layout="centered")
st.title("🧠 Personal AI OS")

# --- PROFILE AUTHENTICATION SYSTEM ---
if "authenticated_profile" not in st.session_state:
    st.session_state.authenticated_profile = None
    st.session_state.current_key = ""
    st.session_state.current_context = ""

if st.session_state.authenticated_profile is None:
    st.subheader("🔒 Secure Profile Gateway")
    st.caption("Enter a password to unlock an existing profile or provision a brand new workspace automatically.")
    
    entered_password = st.text_input("Enter Profile Password", type="password")
    
    if st.button("Unlock / Initialize Workspace"):
        if entered_password:
            if entered_password in profiles:
                # Load existing user profile parameters
                st.session_state.authenticated_profile = entered_password
                st.session_state.current_key = profiles[entered_password].get("api_key", "")
                st.session_state.current_context = profiles[entered_password].get("context", "")
                st.success("Welcome back! Loading secure profile state...")
            else:
                # Initialize a brand new profile workspace dynamically
                profiles[entered_password] = {
                    "api_key": "",
                    "context": "Initialize your custom background here..."
                }
                save_profiles(profiles)
                st.session_state.authenticated_profile = entered_password
                st.session_state.current_key = ""
                st.session_state.current_context = "Initialize your custom background here..."
                st.info("✨ New unique profile detected! Workspace initialized.")
            
            # Reset conversation states
            st.session_state.messages = []
            st.rerun()
        else:
            st.error("Password string cannot be empty.")
    st.stop()

# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
    st.header("⚙️ Profile Config")
    st.success(f"Active Profile Locked")
    
    # 1. API Key Tracking
    api_key_input = st.text_input("Gemini API Key", type="password", value=st.session_state.current_key)
    
    # 2. Context Customization
    context_input = st.text_area("Master Persona Context", value=st.session_state.current_context, height=200)
    
    # Save Action: Commits to local JSON storage instantly
    if st.button("💾 Save Profile Permanently"):
        profiles[st.session_state.authenticated_profile]["api_key"] = api_key_input
        profiles[st.session_state.authenticated_profile]["context"] = context_input
        save_profiles(profiles)
        st.session_state.current_key = api_key_input
        st.session_state.current_context = context_input
        st.success("Saved directly to cloud database storage!")
        
    st.write("---")
    
    # 3. THINKING ARCHITECTURE SELECTOR
    st.subheader("🏎️ Cognitive Architecture")
    architecture = st.selectbox(
        "Choose Engine Strategy:",
        ["Standard Conversation", "Multi-Agent Critic Loop"]
    )
    
    # Logout action
    if st.button("🚪 Lock Workspace"):
        st.session_state.authenticated_profile = None
        st.rerun()

# --- INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat interface history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CONVERSATIONAL RUNTIME ---
if prompt := st.chat_input("Input vector prompt..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state.current_key:
        st.error("⚠️ Workspace active, but no API Key found. Configure via the sidebar panel.")
    else:
        with st.chat_message("model"):
            try:
                client = genai.Client(api_key=st.session_state.current_key)
                
                # Setup master instruction blocks using your configured profile context
                system_instruction = f"""
                You are an elite, highly personalized AI companion. 
                Always adjust your responses using the user's master parameters:
                {st.session_state.current_context}
                """
                
                # ROUTE 1: STANDARD DIRECT CHAT CONVERSATION
                if architecture == "Standard Conversation":
                    with st.spinner("Processing standard pipeline..."):
                        conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
                        final_prompt = f"Previous Chat:\n{conversation_history}\n\nCurrent Request:\n{prompt}"
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=final_prompt,
                            config=types.GenerateContentConfig(system_instruction=system_instruction)
                        )
                        output_text = response.text
                        st.markdown(output_text)
                        
                # ROUTE 2: MULTI-STAGE CRITIC LOOP (The Expert Engine we designed first!)
                elif architecture == "Multi-Agent Critic Loop":
                    status_placeholder = st.empty()
                    
                    passed_evaluation = False
                    iteration = 1
                    max_iterations = 2
                    current_draft = ""
                    feedback = "Initial run. Build a comprehensive deep explanation with expert operational insights."
                    
                    while not passed_evaluation and iteration <= max_iterations:
                        status_placeholder.markdown(f"🔄 **[Critic Loop Iteration {iteration}]** Synthesizing deep draft...")
                        
                        researcher_prompt = f"""
                        {system_instruction}
                        Deconstruct this topic deeply: '{prompt}'.
                        Format with these headers:
                        ## 1. Ground Truth Explanation
                        ## 2. The Insider Perspective (Top 1% Knowledge)
                        ## 3. Alternative Viewpoints
                        ## 4. Operational Action Plan
                        
                        CRITIC FEEDBACK TO RESOLVE: {feedback}
                        """
                        research_response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=researcher_prompt
                        )
                        current_draft = research_response.text
                        
                        status_placeholder.markdown(f"🧐 **[Critic Loop Iteration {iteration}]** Evaluating quality threshold...")
                        evaluator_prompt = f"Analyze this draft regarding '{prompt}'. Return JSON with keys 'score' (int 1-10) and 'critique' (string).\nDraft:\n{current_draft}"
                        
                        eval_response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=evaluator_prompt,
                            config=types.GenerateContentConfig(response_mime_type="application/json")
                        )
                        
                        try:
                            eval_data = json.loads(eval_response.text)
                            score = eval_data.get("score", 0)
                            feedback = eval_data.get("critique", "Enhance precision.")
                        except:
                            score = 8
                            
                        if score >= 8:
                            passed_evaluation = True
                        else:
                            iteration += 1
                    
                    status_placeholder.empty()
                    output_text = current_draft
                    st.markdown(output_text)
                
                # Append finalized model response to tracking records
                st.session_state.messages.append({"role": "model", "content": output_text})
                
            except Exception as e:
                st.error(f"Execution Engine Fault: {e}")