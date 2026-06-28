import streamlit as st
from google import genai
from google.genai import types

# --- SECURITY GATE ---
def check_password():
    if "password_entered" not in st.session_state:
        st.session_state.password_entered = False

    if not st.session_state.password_entered:
        st.warning("🔒 Secure Boot Sequence Initiated.")
        password = st.text_input("Enter Access Code", type="password")
        
        # Checks against the encrypted Streamlit vault
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.password_entered = True
            st.rerun()
        elif password:
            st.error("Access Denied.")
            
        st.stop() # Instantly halts all code execution if password fails

check_password()

# ... (The rest of your original app code goes here) ...
# 1. Page Configuration for Mobile
st.set_page_config(page_title="My Personal OS", page_icon="🧠", layout="centered")
st.title("🧠 Personal AI Companion")

# 2. Initialize Memory (Session State Defaults)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "user_context" not in st.session_state:
    st.session_state.user_context = "I am an electronics and communications engineering student in Bangalore (6th sem). I want to become rich and happy. I like hardware projects."

# 3. The Sidebar Control Center
with st.sidebar:
    st.header("⚙️ Brain Control Center")
    
    # Secure API Key input
    api_key_input = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
    if api_key_input:
        st.session_state.api_key = api_key_input
        
    st.subheader("👤 Master Profile")
    context_input = st.text_area("Who are you?", value=st.session_state.user_context, height=200)
    if st.button("Save Profile Updates"):
        st.session_state.user_context = context_input
        st.success("Profile updated in session!")

    st.write("---")
    st.subheader("🛠️ Behavioral Toggles")
    
    # TOGGLE 1: Access Context
    use_context = st.toggle("Inject Profile Context", value=True, 
                            help="When ON, the AI reads your master profile before answering. When OFF, the AI acts as a generic assistant.")
    
    # TOGGLE 2: Mutate Context
    allow_mutation = st.toggle("Allow Profile Evolution", value=True, 
                               help="When ON, the AI will actively analyze your inputs and ask to modify or update your master profile context.")

# 4. Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Handle Conversations
if prompt := st.chat_input("Ask a question, or share a new thought..."):
    
    # Display user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state.api_key:
        st.error("⚠️ Please enter your API Key in the sidebar menu first.")
    else:
        with st.chat_message("model"):
            with st.spinner("Processing..."):
                try:
                    client = genai.Client(api_key=st.session_state.api_key)
                    
                    # Dynamically build system instructions based on your toggles
                    base_instruction = "You are an elite, highly personalized AI companion. Answer conversationally and match the user's energy."
                    
                    if use_context:
                        base_instruction += f"\n\nHere is the master context about the user to tailor your advice:\n{st.session_state.user_context}"
                    else:
                        base_instruction += "\n\nNOTE: The user has disabled profile context tracking for this message. Respond generally without referencing their background details unless they bring them up explicitly."
                        
                    if allow_mutation:
                        base_instruction += "\n\nCRITICAL RULE: If the user mentions a significant new interest, project, or detail about themselves, explicitly ask at the end of your response if they would like to add this to their master context profile."
                    else:
                        base_instruction += "\n\nCRITICAL RULE: Do NOT ask or suggest modifying the profile context. The user has locked mutations."

                    # Grab recent history context
                    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
                    final_prompt = f"Previous Chat:\n{conversation_history}\n\nCurrent Request:\n{prompt}"
                    
                    # Request generation
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=final_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=base_instruction
                        )
                    )
                    
                    # Display and log the result
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Execution Error: {e}")