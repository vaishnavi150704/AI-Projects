import streamlit as st
from google import genai

# --- CONFIGURATION ---
st.set_page_config(page_title="Multi-Agent Education System", layout="centered")

# Initialize Gemini Client (Use your working key)
# It's safer to put your key in a sidebar or secrets, but we'll keep it here for now
client = genai.Client(api_key = st.secrets["GOOGLE_API_KEY"])
MODEL_ID = "gemini-3.1-flash-lite-preview"

# --- AGENT LOGIC ---
def researcher_agent(topic):
    prompt = f"You are a Researcher. Provide deep scientific facts about {topic}."
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

def writer_agent(raw_data):
    prompt = f"You are a Writer. Turn this into a study guide with bullet points:\n{raw_data}"
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

# --- USER INTERFACE ---
st.title("🎓 Multi-Agent Education System")
st.markdown("Enter a topic below to see the **Researcher** and **Writer** agents collaborate.")

topic = st.text_input("What do you want to learn about?", placeholder="e.g., Photosynthesis")

if st.button("Generate Study Plan"):
    if not topic:
        st.warning("Please enter a topic first!")
    else:
        # Step 1: Researcher Agent
        with st.status("Researcher is sourcing information...", expanded=True) as status:
            research_data = researcher_agent(topic)
            st.write("✅ Research Complete")
            with st.expander("View Raw Research Data"):
                st.write(research_data)
        
        # Step 2: Writer Agent
        with st.status("Writer is synthesizing data...", expanded=True):
            final_output = writer_agent(research_data)
            st.write("✅ Formatting Complete")

        # Display Final Output
        st.success("Study Guide Ready!")
        st.markdown("---")
        st.markdown(final_output)
        
        # Download Button
        st.download_button("Download Study Guide", final_output, file_name=f"{topic}_study_guide.md")
