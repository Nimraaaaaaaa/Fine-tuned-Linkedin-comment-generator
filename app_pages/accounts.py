import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import requests
from datetime import datetime

# Firebase Admin SDK Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate('chatbot-.json')
    firebase_admin.initialize_app(cred)
    db_admin = firestore.client()

# Firebase Client SDK Configuration
config = {
    "apiKey": "Apikey",
    "authDomain": "firebaseapp.com",
    "projectId": "chatbot",
    "storageBucket": "chatbot",
    "databaseURL": "https://chatbot.com",
    "messagingSenderId": "31",
    "appId": "1:33261:web:d49bc",
    "measurementId": "G-WC"
}
firebase = pyrebase.initialize_app(config)
firebase_auth = firebase.auth()

FASTAPI_URL = "https://ahad-backend.onrender.com"  # Base FastAPI URL

def signup(email, password, username):
    try:
        user = firebase_auth.create_user_with_email_and_password(email, password)
        user_id = user['localId']
        firebase_auth.update_profile(user['idToken'], display_name=username)
        user_data = {
            "email": email,
            "username": username,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_login": firestore.SERVER_TIMESTAMP,
            "comments": [],
            "chat_sessions": []  # Initialize with chat_sessions instead of chat_interactions
        }
        db_admin.collection("users").document(user_id).set(user_data)
        st.success('🎉 Account Created Successfully!')
        st.markdown('Please login using your email and password')
        st.balloons()
    except Exception as e:
        st.error(f'❌ Signup Failed! {str(e)}')

def login(email, password):
    try:
        user = firebase_auth.sign_in_with_email_and_password(email, password)
        user_id = user['localId']
        db_admin.collection("users").document(user_id).update({"last_login": firestore.SERVER_TIMESTAMP})
        
        # Fetch chat sessions from Firestore
        user_data = db_admin.collection("users").document(user_id).get()
        if user_data.exists:
            chat_sessions = user_data.to_dict().get("chat_sessions", [])
            st.session_state.chat_sessions = chat_sessions  # Load chat sessions into session state
            # Do not set an active session ID here to force a new session
        else:
            st.session_state.chat_sessions = []

        st.session_state["user_id"] = user_id
        st.session_state.signedout = False
        st.session_state.active_session_id = None  # Reset to ensure a new session on first query
        st.session_state.page = "chatbot"  # Set page to chatbot after login
        st.success('✅ Login Successful!')
        st.rerun()
    except Exception as e:
        st.error(f'❌ Login Failed! {str(e)}')

def logout():
    st.session_state.signedout = True
    st.session_state.username = ''
    st.session_state.active_session_id = None
    st.session_state.chat_sessions = []
    st.success("👋 Logged out successfully!")
    st.rerun()

def chatbot_interface():
    st.title("What can I help with?")

    

    # Initialize chat sessions and active session in session state if not present
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []
    if "active_session_id" not in st.session_state:
        st.session_state.active_session_id = None

    # Sidebar for chat sessions
    with st.sidebar:
        st.header("Chat Sessions")
        if st.session_state.chat_sessions:
            for i, session in enumerate(st.session_state.chat_sessions):
                first_query = session["queries"][0]["user_query"] if session["queries"] else "Empty Session"
                if st.button(f"Session {i + 1}: {first_query[:30]}..."):
                    st.session_state.active_session_id = session["session_id"]
        else:
            st.write("No chat sessions available.")
        
        # Button to start a new session
        if st.button("➕ New Chat Session"):
            st.session_state.active_session_id = None  # Reset to create a new session
            st.rerun()

           

    # Display the active session's chat history
    if st.session_state.active_session_id:
        for session in st.session_state.chat_sessions:
            if session["session_id"] == st.session_state.active_session_id:
                
                for chat in session["queries"]:
                    st.write(f"**You:** {chat['user_query']}")
                    st.write(f"**Bot:** {chat['bot_response']}")
                    st.write("---")
                break
    

    # User input for new chat
    user_query = st.chat_input("Type your message...")
    if user_query:
        st.write(f"**You:** {user_query}")
        
        try:
            # Send query to FastAPI with user_id and session_id (if exists)
            payload = {
                "query": user_query,
                "user_id": st.session_state["user_id"],
            }
            if st.session_state.active_session_id:
                payload["session_id"] = st.session_state.active_session_id

            response = requests.post(f"{FASTAPI_URL}/chatbot/", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result.get("response", "⚠️ No response received.")
                returned_session_id = result.get("session_id")
                
                # Update active session ID if a new one is returned
                if not st.session_state.active_session_id:
                    st.session_state.active_session_id = returned_session_id

                # Update local chat sessions
                session_found = False
                for session in st.session_state.chat_sessions:
                    if session["session_id"] == returned_session_id:
                        session["queries"].append({
                            "user_query": user_query,
                            "bot_response": bot_response,
                            "timestamp": datetime.now()
                        })
                        session_found = True
                        break
                if not session_found:
                    st.session_state.chat_sessions.append({
                        "session_id": returned_session_id,
                        "queries": [{
                            "user_query": user_query,
                            "bot_response": bot_response,
                            "timestamp": datetime.now()
                        }],
                        "created_at": datetime.now()
                    })

            else:
                bot_response = f"⚠️ API Error! Status Code: {response.status_code}"
        except Exception as e:
            bot_response = f"⚠️ Error: {str(e)}"

        # Display the bot's response
        st.write(f"**Bot:** {bot_response}")
    
    

def app():
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'signedout' not in st.session_state:
        st.session_state.signedout = True
    if st.session_state.signedout:
        st.title(" Login / Signup Page")
        choice = st.selectbox('Select Option:', ['Login', 'Signup'])
        if choice == 'Signup':
            email = st.text_input('📧 Email')
            password = st.text_input('🔑 Password', type='password')
            username = st.text_input('👤 Username')
            if st.button('📝 Create Account'):
                signup(email, password, username)
        else:
            email = st.text_input('📧 Email')
            password = st.text_input('🔑 Password', type='password')
            if st.button('Login'):
                login(email, password)
    else:
        chatbot_interface()

if __name__ == "__main__":
    app()
