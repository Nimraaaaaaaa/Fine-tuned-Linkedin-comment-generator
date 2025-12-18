import streamlit as st
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv

# Correcting the imports for accounts and comments
from app_pages import comments, accounts

load_dotenv()

st.set_page_config(
    page_title="Your App",
    page_icon="🖥️",
    initial_sidebar_state="collapsed"
)

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def logout(self):
        st.session_state.signedout = True
        st.session_state.username = ''
        st.session_state.active_session_id = None
        st.session_state.chat_sessions = []
        st.session_state.page = "accounts"  # Set page to redirect to accounts.py
        st.success("👋 Logged out successfully!")
        st.rerun()

    def run(self):
        with st.sidebar:
            # Hide "My App" menu title
            st.markdown(
                """
                <style>
                .css-1d391kg {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Sidebar options (Settings removed)
            app = option_menu(
                menu_title=None,  # Remove menu title
                options=['Comments', 'Accounts'],  # Home removed
                icons=['chat-fill', 'person-fill'],  # Home icon removed
                menu_icon='chat-text-fill',
                default_index=1,  # Accounts page will open by default (index 1 now)
                styles={
                    "container": {
                        "padding": "5!important",
                        "background-color": "#f0f2f6",  # Light gray background for the sidebar
                        "height": "100vh"
                    },
                    "icon": {"color": "black", "font-size": "18px"},  # Black icons
                    "nav-link": {
                        "color": "black",  # Black text for menu items
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "5px 0",
                        "padding": "10px",
                        "border-radius": "5px",
                        "--hover-color": "#e0e0e0"  # Light gray hover color
                    },
                    "nav-link-selected": {
                        "background-color": "#4CAF50",  # Green background for selected item
                        "color": "white",  # White text for selected item
                        "font-weight": "bold"
                    },
                }
            )

            # Logout Button (Directly in Sidebar)
            if st.button('🚪 Logout'):
                self.logout()

        if app == "Comments":
            comments.app()
        elif app == "Accounts":
            accounts.app()

# Instantiate and run the app
multi_app = MultiApp()
multi_app.run()
