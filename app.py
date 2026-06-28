import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration (Makes it look great on a phone browser)
st.set_page_config(page_title="My AI OS", page_icon="🧠", layout="centered")
st.title("🧠 Personal AI Companion")

# 2. Initialize Memory (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "user_context" not in st.session_state:
    st.session_state.user_context = "I am an electronics and communications engineering student in Bangalore (6th sem). I want to become rich and happy. I like hardware projects."

# 3. The Sidebar (Where you paste your ChatGPT context)
with st.sidebar:
    st.header("⚙️ Brain Settings")
    
    # Secure API Key input
    api_key_input = st.text_input("Gemini API Key", type="password", value=st.session_state.api_key)
    if api_key_input:
        st.session_state.api_key = api_key_input
        
    st.subheader("👤 Your Profile (Context)")
    st.caption("Paste your full ChatGPT context here. The AI reads this before every reply.")
    
    # Text area for the master context
    context_input = st.text_area("Who are you?", value=st.session_state.user_context, height=300)
    if st.button("Save Profile"):
        st.session_state.user_context = context_input
        st.success("Context secured!")

# 4. Render the Chat History on screen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. The Chat Input box (Fixed to the bottom of your phone screen)
if prompt := st.chat_input("Ask a question, or share a new thought..."):
    
    # Display user's new message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6. Generate the AI Response
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your API Key in the sidebar menu first.")
    else:
        with st.chat_message("model"):
            with st.spinner("Thinking..."):
                try:
                    client = genai.Client(api_key=st.session_state.api_key)
                    
                    # The System Instructions (Rules for the AI)
                    system_instruction = f"""
                    You are an elite, highly personalized AI companion. 
                    Here is the master context about the user:
                    {st.session_state.user_context}
                    
                    RULES:
                    1. Answer conversationally, mirroring the user's energy.
                    2. ALWAYS tailor your advice using their master context.
                    3. If the user mentions a new interest, goal, project, or fact about themselves that isn't in their master context, explicitly ask them at the end of your reply: "Would you like me to remind you to add this to your sidebar profile?"
                    """
                    
                    # Combine history and current prompt so it remembers the flow
                    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
                    final_prompt = f"Previous Chat:\n{conversation_history}\n\nCurrent Request:\n{prompt}"
                    
                    # Call the API
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=final_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        )
                    )
                    
                    # Display and save the response
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Something went wrong: {e}")