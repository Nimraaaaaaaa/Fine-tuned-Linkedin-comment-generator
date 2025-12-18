from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin.exceptions import FirebaseError
from pydantic import BaseModel, EmailStr
from datetime import datetime
from dotenv import load_dotenv
import os
import openai
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from memory_engine import MemoryEngine
from human_style_generator import HumanStyleGenerator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

# Get API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API Key is missing! Please check your .env file.")

import openai
openai.api_key = OPENAI_API_KEY


app = FastAPI()

# Initialize ChromaDB and MemoryEngine
vectordb = Chroma(persist_directory="./chroma_style_db", embedding_function=OpenAIEmbeddings())
memory_engine = MemoryEngine()
human_style_generator = HumanStyleGenerator()

# Firebase Initialization
try:
    cred_path = "chatbot_.json"
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Firebase credentials file '{cred_path}' not found.")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()
except Exception as e:
    print(f"Firebase initialization error: {e}")
    exit()

# Pydantic Models
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str

class CommentRequest(BaseModel):
    comment: str
    user_id: str

class ChatbotRequest(BaseModel):
    query: str
    user_id: str
    session_id: str = None  # Optional session_id, will create new if not provided

class ChatSession(BaseModel):
    session_id: str
    queries: list = []

# ✅ Function to fetch user data from Firestore (unchanged)
async def fetch_user_data(user_id: str, field: str):
    """Fetches specific field data (comments or chat history) for a given user."""
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            return []

        return user_data.to_dict().get(field, [])
    except Exception as e:
        print(f"Error fetching {field}: {e}")
        return []

# Modified helper function to manage sessions (creates new session by default if no session_id provided)
async def get_or_create_session(user_id: str, session_id: str = None):
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            raise HTTPException(status_code=404, detail="User not found")

        user_dict = user_data.to_dict()
        sessions = user_dict.get("chat_sessions", [])

        # If no session_id is provided, always create a new session (for login/signup scenario)
        if not session_id:
            new_session_id = str(datetime.now().timestamp())
            new_session = {
                "session_id": new_session_id,
                "queries": [],
                "created_at": datetime.now()
            }
            sessions.append(new_session)
            user_ref.update({"chat_sessions": sessions})
            return new_session_id
        
        # If session_id is provided, find and return it
        for session in sessions:
            if session["session_id"] == session_id:
                return session["session_id"]
        
        # If session_id is provided but not found, create a new session
        new_session_id = str(datetime.now().timestamp())
        new_session = {
            "session_id": new_session_id,
            "queries": [],
            "created_at": datetime.now()
        }
        sessions.append(new_session)
        user_ref.update({"chat_sessions": sessions})
        return new_session_id
    except Exception as e:
        print(f"Error in session management: {e}")
        raise HTTPException(status_code=500, detail="Session management error")

# Modified fetch_session_data for sessions
async def fetch_session_data(user_id: str, session_id: str):
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            return []

        sessions = user_data.to_dict().get("chat_sessions", [])
        for session in sessions:
            if session["session_id"] == session_id:
                return session["queries"]
        return []
    except Exception as e:
        print(f"Error fetching session data: {e}")
        return []

# API Endpoints
@app.post("/signup/")
async def signup(user: UserSignup):
    try:
        new_user = auth.create_user(email=user.email, password=user.password)
        user_ref = db.collection("users").document(new_user.uid)
        user_ref.set({
            "email": user.email,
            "name": user.name,
            "created_at": datetime.now(),
            "comments": [],
            "chat_sessions": []  # Changed from chat_interactions to chat_sessions
        })
        return {"message": "User created successfully", "user_id": new_user.uid}
    except FirebaseError as e:
        print(f"Firebase error: {e}")
        raise HTTPException(status_code=500, detail="Error creating user in Firebase")
    except Exception as e:
        print(f"Error signing up: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/save_comment/")
async def save_comment(request: CommentRequest):
    try:
        # Remove pattern/quality check to allow saving any comment
        user_ref = db.collection("users").document(request.user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            raise HTTPException(status_code=404, detail="User not found")

        comment_data = {
            "comment": request.comment,
            "timestamp": datetime.now()
        }
        user_ref.update({"comments": firestore.ArrayUnion([comment_data])})

        # Add the comment to ChromaDB for future context retrieval
        try:
            vectordb.add_texts([request.comment])
            vectordb.persist()
        except Exception as e:
            print(f"ChromaDB add error: {e}")
            # Do not fail the request if ChromaDB update fails

        return {"message": "Comment saved successfully"}
    except Exception as e:
        print(f"Error saving comment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/get_comments/{user_id}")
async def get_comments(user_id: str):
    comments = await fetch_user_data(user_id, "comments")
    return {"comments": comments}

@app.delete("/delete_comment/{user_id}/{comment_index}")
async def delete_comment(user_id: str, comment_index: int):
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            raise HTTPException(status_code=404, detail="User not found")

        user_dict = user_data.to_dict()
        comments = user_dict.get("comments", [])

        if not comments or comment_index < 0 or comment_index >= len(comments):
            raise HTTPException(status_code=400, detail="Invalid comment index")

        del comments[comment_index]
        user_ref.update({"comments": comments})

        return {"message": "Comment deleted successfully"}
    except Exception as e:
        print(f"Error deleting comment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chatbot/")
async def chatbot(request: ChatbotRequest):
    try:
        # 1. Session management (Firebase): get or create session for user
        session_id = await get_or_create_session(request.user_id, request.session_id)
        post_id = session_id  # Use session_id as post_id for memory tracking

        # 2. Fetch session queries and user-saved comments (Firebase)
        session_queries = await fetch_session_data(request.user_id, session_id)
        saved_comments = await fetch_user_data(request.user_id, "comments")

        # --- NEW: Find most similar saved comment to the query ---
        def get_most_similar_saved_comment(query, saved_comments):
            if not saved_comments:
                return None
            comments_text = [c['comment'] if isinstance(c, dict) and 'comment' in c else c for c in saved_comments]
            vectorizer = TfidfVectorizer().fit([query] + comments_text)
            vectors = vectorizer.transform([query] + comments_text)
            sims = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
            best_idx = sims.argmax()
            return comments_text[best_idx]

        best_saved_comment = get_most_similar_saved_comment(request.query, saved_comments)
        best_saved_style = None
        if best_saved_comment:
            best_saved_style = human_style_generator.extract_properties_from_comments([best_saved_comment]).get('style')

        # --- Aggregate style from all saved comments ---
        aggregate_saved_comment_props = human_style_generator.extract_properties_from_comments(saved_comments)
        aggregate_saved_style = aggregate_saved_comment_props.get('style')
        theme = aggregate_saved_comment_props.get('theme', 'LinkedIn Professionalism')
        sentiment = aggregate_saved_comment_props.get('sentiment', 'Professional')
        avg_length = aggregate_saved_comment_props.get('avg_length')

        # 3. Retrieve a style reference comment from ChromaDB using the query
        sample_comments = []
        sample_style = None
        try:
            results = vectordb.similarity_search(request.query, k=2)
            if results:
                sample_comments = [r.page_content for r in results[:2]]
                sample_style = human_style_generator.extract_properties_from_comments(sample_comments).get('style')
        except Exception as e:
            print(f"ChromaDB retrieval error: {e}")
        if not sample_comments:
            sample_comments = ["Great insight!", "This really resonates with me."]

        # 4. Combine up to 2 saved and 2 sample comments for the prompt
        all_prompt_comments = []
        if saved_comments:
            all_prompt_comments.extend([c['comment'] if isinstance(c, dict) and 'comment' in c else c for c in saved_comments[:2]])
        if sample_comments:
            all_prompt_comments.extend(sample_comments[:2])

        # 5. Build flexible prompt (mention both styles)
        prompt = f"""
You are a human social media user. Write a short, natural, and relevant comment for the following post.\n\nPost:\n{request.query}\n\nBelow are some example comments. Try to match their style and length, but it's okay if your response is not a perfect match.\n\nExample Comments:\n"""
        for c in all_prompt_comments:
            prompt += f"- {c}\n"
        prompt += f"\nConstraints:\n- Try to match the structure and style of the above comments.\n- If possible, match the style of the most similar saved comment to the post.\n- Otherwise, match the overall style of your saved comments.\n- Target length: about {avg_length} words (±5 is OK).\n- Avoid these words: {', '.join(list(human_style_generator.ai_banned_words))}\n"

        print("Prompt being sent to OpenAI:", prompt)

        # 6. Call OpenAI to generate the comment with flexible validation
        max_attempts = 3
        best_response = None
        best_score = -1
        banned_words = list(human_style_generator.ai_banned_words)
        for attempt in range(max_attempts):
            try:
                response = openai.ChatCompletion.create(
                    model="ft:gpt-4o-2024-08-06:ahad-iqbal:custom-gpt:BSTaq1X0",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    timeout=20
                )
            except openai.error.OpenAIError as e:
                print("OpenAI API error:", e)
                continue

            if not response.choices or not response.choices[0].message.content.strip():
                continue

            ai_response = response.choices[0].message.content.strip()
            score = 0
            # 1. Banned words
            if not any(bw.lower() in ai_response.lower() for bw in banned_words):
                score += 1
            # 2. Length (±5 words)
            if avg_length:
                word_count = len(ai_response.split())
                if abs(word_count - avg_length) <= 5:
                    score += 1
            else:
                score += 1
            # 3. Style (prefer best match, then aggregate, then sample)
            style_to_check = best_saved_style or aggregate_saved_style or sample_style
            style_valid = True
            if style_to_check:
                if style_to_check.get('has_emoji'):
                    style_valid = any(char in ai_response for char in '😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚🙂🤗🤩🤔🤨😐😑😶🙄😏😣😥😮🤐😯😪😫😴😌😛😜😝🤤😒😓😔😕🙃🤑😲☹️🙁😖😞😟😤😢😭😦😧😨😩🤯😬😰😱🥵🥶😳🤪😵😡😠🤬😷🤒🤕🤢🤮🤧😇🥳🥺🤠🤡🤥🤫🤭🧐🤓😈👿👹👺💀👻👽👾🤖😺😸😹😻😼😽🙀😿😾')
                if style_valid and style_to_check.get('has_exclamation'):
                    style_valid = '!' in ai_response
                if style_valid and style_to_check.get('has_question'):
                    style_valid = '?' in ai_response
            if style_valid:
                score += 1
            if score > best_score:
                best_score = score
                best_response = ai_response
            if score == 3:
                break  # All checks passed

        # 7. Fallback if nothing matches
        if not best_response:
            best_response = all_prompt_comments[0] if all_prompt_comments else "Thanks for sharing!"

        # 8. Save to Firebase as before (for user history)
        user_ref = db.collection("users").document(request.user_id)
        chat_data = {
            "user_query": request.query,
            "bot_response": best_response,
            "timestamp": datetime.now()
        }
        user_data = user_ref.get().to_dict()
        sessions = user_data.get("chat_sessions", [])
        for session in sessions:
            if session["session_id"] == session_id:
                session["queries"].append(chat_data)
                break
        user_ref.update({"chat_sessions": sessions})

        return {"response": best_response, "session_id": session_id}

    except Exception as e:
        print("General chatbot error:", e)
        return {"response": "Thanks for sharing!", "session_id": None, "warning": "AI error, fallback used."}
