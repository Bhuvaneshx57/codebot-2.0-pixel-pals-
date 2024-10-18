import streamlit as st
from groq import Groq
from pinecone import Pinecone
import requests

# Initialize Groq and Pinecone clients
client = Groq(api_key="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")
pc = Pinecone(api_key="b311901d-a6a4-4b0a-a292-9431183d5623")
index = pc.Index("quickstart")

# API keys
CARBON_API_KEY = "KACSBQ0vmPT6uy53sPOw"  # Carbon Interface API
OPENAQ_API_KEY = "b5afc21364c58b4f861f3b8dbc6fb4bd29f2e794f4eedb46d2dd80319aed89eb"  # OpenWeather API key
NREL_API_KEY = "1I4GaPFBQO7v72D7IXCZ6MSV9NR4a5odh7dcDsyi"  # National Renewable Energy Laboratory API key

# Set the API key in session state
st.session_state.api_key = "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"

# Environment-friendly theme settings


# Title and header section with eco-friendly visuals
st.markdown("<h1 style='color: #2ecc71; text-align: center'>🌍 Eco-Chat: Environment-Friendly Assistant</h1>", unsafe_allow_html=True)


st.markdown("<p style='color: #2ecc71; text-align: center' >Helping you make sustainable choices while staying connected to the environment!</p>", unsafe_allow_html=True)

# Only show the API key input if the key is not already set
if not st.session_state.api_key:
    api_key = st.text_input("Enter API Key", type="password")
    if api_key:
        st.session_state.api_key = api_key
        st.experimental_rerun()  # Refresh the app once the key is entered to remove the input field
else:

    
    # Initialize chat message list in session state if it doesn't exist
    if "chat_messages" not in st.session_state:
        st.session_state.groq_chat_messages = [{"role": "system", "content": "You are a helpful assistant. The user will ask a query, and you will respond to it. **Tip:** Aim for a conversational tone that balances informative content with humor. Make it engaging and relatable, so readers feel inspired to take action while having a good laugh!"}]
        st.session_state.chat_messages = []

    # Display previous chat messages
    for messages in st.session_state.chat_messages:
        if messages["role"] in ["user", "assistant"]:
            with st.chat_message(messages["role"]):
                st.markdown(f"<p style='color: #fbffff ;'>{messages['content']}</p>", unsafe_allow_html=True)

    # Handle user input and get response
    def get_chat():
        # Embedding and querying with Pinecone
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[st.session_state.chat_messages[-1]["content"]],
            parameters={"input_type": "query"}
        )
        results = index.query(
            namespace="ns1",
            vector=embedding[0].values,
            top_k=3,
            include_values=False,
            include_metadata=True
        )
        
        context = ""
        for result in results.matches:
            if result['score'] > 0.8:
                context += result['metadata']['text']
        
        st.session_state.groq_chat_messages[-1]["content"] = f"User Query: {st.session_state.chat_messages[-1]['content']} \n Retrieved Content (optional): {context}"
        
        chat_completion = client.chat.completions.create(
            messages=st.session_state.groq_chat_messages,
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content

    # API functions
    def get_carbon_data():
        response = requests.get(
            "https://api.carboninterface.com/v1/estimations",
            headers={"Authorization": f"Bearer {CARBON_API_KEY}"}
        )
        return response.json()

    def get_weather_data(city):
        response = requests.get(
            f"https://api.openaq.org/v2/latest?city={city}&appid={OPENAQ_API_KEY}&units=metric"
        )
        return response.json()

    def get_energy_data():
        response = requests.get(
            f"https://api.nrel.gov/v1/some_endpoint?api_key={NREL_API_KEY}"
        )
        return response.json()

    # Handle user input
    if prompt := st.chat_input("Try asking about sustainable choices or thank the assistant for its help!"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.groq_chat_messages.append({"role": "user", "content": prompt})

        with st.spinner("🌱 Fetching eco-friendly insights..."):
            response = get_chat()
        with st.chat_message("assistant"):
            st.markdown(f"<p style='color: #fbffff ;'>{response}</p>", unsafe_allow_html=True)
        
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.session_state.groq_chat_messages.append({"role": "assistant", "content": response})