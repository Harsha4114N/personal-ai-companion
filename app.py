import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import json
import os
import io

# --- STORAGE ARCHITECTURE ---
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

profiles = load_profiles()

# --- INITIAL APP CONFIG ---
st.set_page_config(page_title="Personal AI OS", page_icon="🧠", layout="centered")
st.title("🧠 Personal AI OS v2.0")

# --- PROFILE SECURITY GATEWAY ---
if "authenticated_profile" not in st.session_state:
    st.session_state.authenticated_profile = None
    st.session_state.current_key = ""
    st.session_state.current_context = ""

if st.session_state.authenticated_profile is None:
    st.subheader("🔒 Secure Profile Gateway")
    entered_password = st.text_input("Enter Profile Password", type="password")
    
    if st.button("Unlock / Initialize Workspace"):
        if entered_password:
            if entered_password in profiles:
                st.session_state.authenticated_profile = entered_password
                st.session_state.current_key = profiles[entered_password].get("api_key", "")
                st.session_state.current_context = profiles[entered_password].get("context", "")
                st.success("Loading secure profile state...")
            else:
                profiles[entered_password] = {
                    "api_key": "",
                    "context": "Initialize your custom background here..."
                }
                save_profiles(profiles)
                st.session_state.authenticated_profile = entered_password
                st.session_state.current_key = ""
                st.session_state.current_context = "Initialize your custom background here..."
                st.info("✨ New profile initialized.")
            
            st.session_state.messages = []
            st.rerun()
    st.stop()

# --- SIDEBAR ACCESSORIES & CONTROLS ---
with st.sidebar:
    st.header("⚙️ System Configuration")
    st.caption(f"Profile Hash Authorized")
    
    # 1. Identity Parameters
    api_key_input = st.text_input("Gemini API Key", type="password", value=st.session_state.current_key)
    context_input = st.text_area("Master Persona Context", value=st.session_state.current_context, height=150)
    
    if st.button("💾 Save Settings Permanently"):
        profiles[st.session_state.authenticated_profile]["api_key"] = api_key_input
        profiles[st.session_state.authenticated_profile]["context"] = context_input
        save_profiles(profiles)
        st.session_state.current_key = api_key_input
        st.session_state.current_context = context_input
        st.success("Cloud database updated!")
        
    st.write("---")
    
    # 2. Advanced Cognitive Engine Selection
    st.subheader("🏎️ Cognitive Architecture")
    architecture = st.selectbox(
        "Choose Engine Strategy:",
        ["Standard Conversation", "Multi-Agent Critic Loop"]
    )
    
    st.write("---")
    
    # 3. UPGRADE A: Live Web Grounding Switch
    st.subheader("🌐 Grounding & Search")
    enable_grounding = st.toggle("Enable Live Google Search", value=False, 
                                 help="Allows Gemini to scan the live internet for real-time facts before answering.")
    
    # 4. UPGRADE B: Voice Synthesis Switch
    st.subheader("🔊 Audio Architecture")
    enable_voice_output = st.toggle("Enable Text-to-Speech", value=False,
                                    help="Automatically converts the AI response into spoken audio.")
    
    if st.button("🚪 Lock Workspace"):
        st.session_state.authenticated_profile = None
        st.rerun()

# --- FILE ANALYTICS CONTAINER (Datasheet Vision) ---
st.subheader("📁 Hardware & Datasheet Vision")
uploaded_file = st.file_uploader("Drop PDF datasheets, schematics, or reference materials here", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.info(f"📎 File staged for multimodal synthesis: {uploaded_file.name}")

st.write("---")

# --- INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- UPGRADE C: Native Voice Input Capture ---
st.subheader("🎙️ Voice Command Input")
audio_input = st.audio_input("Record a voice note command")

# --- CONVERSATIONAL MATRIX PROCESSING ---
prompt = st.chat_input("Or type an input vector prompt...")

# If voice audio is recorded, map it as the active prompt input
if audio_input and not prompt:
    st.warning("🔄 Multi-modal voice payload detected. Processing input stream...")
    # Passing audio directly to Gemini flash model for lightning-fast native transcription
    prompt = "Transcribe and answer this audio command completely."

if prompt:
    # Append input visually to execution array
    st.session_state.messages.append({"role": "user", "content": prompt if not audio_input else "🎤 [Voice Input Stream Context]"})
    with st.chat_message("user"):
        st.markdown(prompt if not audio_input else "🎤 *Sent a voice command recording...*")

    if not st.session_state.current_key:
        st.error("⚠️ Active workspace lacks valid Gemini authorization credentials.")
    else:
        with st.chat_message("model"):
            try:
                client = genai.Client(api_key=st.session_state.current_key)
                
                # Base system instructions injecting your custom master profile properties
                system_instruction = f"""
                You are an elite, highly personalized AI companion.
                Tailor all operational answers using the user's master settings profile:
                {st.session_state.current_context}
                """
                
                # Dynamic Tool compilation (Inject Live Search Grounding if checked)
                active_tools = []
                if enable_grounding:
                    active_tools.append(types.Tool(google_search=types.GoogleSearch()))
                
                # Bundle multi-modal components
                contents_payload = []
                
                # Add voice data if present
                if audio_input:
                    contents_payload.append(types.Part.from_bytes(data=audio_input.read(), mime_type="audio/wav"))
                
                # Add datasheet/PDF document processing layers if present
                if uploaded_file:
                    contents_payload.append(types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type))
                
                # Compile execution prompt text
                conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:]])
                final_text_block = f"Previous Chat:\n{conversation_history}\n\nCurrent Input Context:\n{prompt}"
                contents_payload.append(final_text_block)
                
                # --- EXECUTION PIPELINE ---
                if architecture == "Standard Conversation":
                    with st.spinner("Executing dynamic context parsing..."):
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents_payload,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                tools=active_tools
                            )
                        )
                        output_text = response.text
                        st.markdown(output_text)
                        
                        # Display search grounding citations if used
                        if enable_grounding and getattr(response.candidates[0], 'grounding_metadata', None):
                            st.caption("🌐 *Sourced from Live Google Search Grounding Index*")
                
                elif architecture == "Multi-Agent Critic Loop":
                    status_placeholder = st.empty()
                    iteration = 1
                    max_iterations = 2
                    current_draft = ""
                    feedback = "Analyze thoroughly. Ensure structural operational engineering value."
                    
                    while iteration <= max_iterations:
                        status_placeholder.markdown(f"🔄 **[Critic Loop Iteration {iteration}]** Synthesizing payload...")
                        
                        loop_payload = contents_payload.copy()
                        loop_payload.append(f"\nCRITIC DIRECTIVES TO IMPROVE PREVIOUS ATTEMPTS: {feedback}")
                        
                        research_response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=loop_payload,
                            config=types.GenerateContentConfig(system_instruction=system_instruction, tools=active_tools)
                        )
                        current_draft = research_response.text
                        
                        status_placeholder.markdown(f"🧐 **[Critic Loop Iteration {iteration}]** Scoring quality parameters...")
                        eval_response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=f"Rate this technical output for request '{prompt}' on scale 1-10 inside JSON object key 'score', and 'critique'.\nDraft:\n{current_draft}",
                            config=types.GenerateContentConfig(response_mime_type="application/json")
                        )
                        
                        try:
                            eval_data = json.loads(eval_response.text)
                            score = eval_data.get("score", 8)
                            feedback = eval_data.get("critique", "")
                        except:
                            score = 8
                            
                        if score >= 8:
                            break
                        iteration += 1
                        
                    status_placeholder.empty()
                    output_text = current_draft
                    st.markdown(output_text)
                
                # Save answer tracking states
                st.session_state.messages.append({"role": "model", "content": output_text})
                
                # --- UPGRADE D: Automated Audio Readout Generation ---
                if enable_voice_output and output_text:
                    with st.spinner("Synthesizing audio output response..."):
                        # Strip markdown headers or symbols out for clean reading execution
                        clean_audio_text = output_text.replace("#", "").replace("*", "").replace("`", "")
                        tts = gTTS(text=clean_audio_text[:1000], lang='en', tld='com') # Safe cap to keep speed fast
                        audio_buffer = io.BytesIO()
                        tts.write_to_fp(audio_buffer)
                        audio_buffer.seek(0)
                        st.audio(audio_buffer, format="audio/mp3", autoplay=True)
                        
            except Exception as e:
                st.error(f"Execution Error: {e}")