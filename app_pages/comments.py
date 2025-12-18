import streamlit as st
import requests


def fetch_comments(user_id):
    try:
        api_url = f"http://127.0.0.1:8000/get_comments/{user_id}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            # Each comment is a dict with 'comment' and 'timestamp'
            return [c['comment'] for c in data.get('comments', [])]
    except Exception:
        pass
    return []

def save_comment(user_id, comment):
    api_url = "http://127.0.0.1:8000/save_comment/"
    payload = {"comment": comment, "user_id": user_id}
    try:
        response = requests.post(api_url, json=payload)
        return response.status_code == 200
    except Exception:
        return False

def delete_comment(user_id, idx):
    api_url = f"http://127.0.0.1:8000/delete_comment/{user_id}/{idx}"
    try:
        response = requests.delete(api_url)
        return response.status_code == 200
    except Exception:
        return False

def app():
    st.markdown("""
        <style>
        .comment-card {
            background: #23272f;
            border-radius: 18px;
            padding: 18px 16px 10px 16px;
            margin-bottom: 22px;
            box-shadow: 0 4px 16px rgba(44,62,80,0.10);
            border: none;
            color: #fff !important;
            transition: box-shadow 0.2s;
        }
        .comment-card:focus-within {
            box-shadow: 0 0 0 2px #4CAF50;
        }
        .comment-label {
            font-weight: 600;
            color: #fff !important;
            font-size: 17px;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }
        .stTextArea textarea {
            background: #23272f !important;
            border-radius: 10px !important;
            color: #fff !important;
            border: 1.5px solid #444 !important;
            font-size: 15px !important;
            transition: border 0.2s;
        }
        .stTextArea textarea:focus {
            border: 1.5px solid #4CAF50 !important;
        }
        .save-btn {
            background: #4CAF50;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 6px 18px;
            font-weight: 600;
            margin-top: 8px;
            cursor: pointer;
        }
        .add-btn {
            background: #23272f;
            color: #4CAF50;
            border: 2px dashed #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px auto;
            cursor: pointer;
        }
        .delete-btn {
            background: #ff4d4f;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 2px 10px;
            font-weight: 600;
            margin-left: 10px;
            cursor: pointer;
            float: right;
        }
        </style>
    """, unsafe_allow_html=True)

    # Heading and subtitle
    st.markdown("""
        <h2 style='color:#fff; font-weight: 800; margin-bottom: 8px;'>Sample Comments</h2>
        <div style='color:#fff; font-weight: 600; font-size: 17px; margin-bottom: 28px;'>You can save your favorite sample comments here for quick reuse and inspiration.</div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please login to manage your comments.")
        return

    # Load comments from backend only once per session or after save/delete
    if "comments" not in st.session_state or st.session_state.get("reload_comments"):
        st.session_state.comments = fetch_comments(user_id)
        st.session_state.reload_comments = False

    comments = st.session_state.comments
    updated_comments = []
    delete_indices = []

    for i, comment in enumerate(comments):
        st.markdown(f"<div class='comment-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            new_val = st.text_area(f"Comment {i+1}", value=comment, key=f"comment_{i+1}", height=80, label_visibility="collapsed")
            updated_comments.append(new_val)
        with col2:
            if st.button("🗑️", key=f"delete_{i}", help="Delete this comment"):
                delete_indices.append(i)
        st.markdown("</div>", unsafe_allow_html=True)

    # Delete comments if any
    if delete_indices:
        for idx in sorted(delete_indices, reverse=True):
            if delete_comment(user_id, idx):
                st.session_state.reload_comments = True
        st.rerun()

    # Add new comment button (replaces the + button)
    add_btn_style = """
        <style>
        .add-comment-btn {
            background: #4CAF50;
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 10px 28px;
            font-size: 17px;
            font-weight: 700;
            margin: 18px auto 18px auto;
            display: block;
            transition: background 0.2s;
            box-shadow: 0 2px 8px rgba(44,62,80,0.10);
            cursor: pointer;
        }
        .add-comment-btn:hover {
            background: #388e3c;
        }
        </style>
    """
    st.markdown(add_btn_style, unsafe_allow_html=True)
    if st.button("Add New Comment", key="add_comment", help="Add new comment"):
        updated_comments.append("")
        st.session_state.comments = updated_comments
        st.rerun()

    # Save all comments
    if st.button("💾 Save All", key="save_all", help="Save all comments"):
        all_success = True
        for comment in updated_comments:
            if comment.strip():
                if not save_comment(user_id, comment):
                    all_success = False
        st.session_state.reload_comments = True
        if all_success:
            st.success("All comments saved successfully!")
        else:
            st.error("Some comments could not be saved. Please try again.")
        st.rerun()

if __name__ == "__main__":
    app()
