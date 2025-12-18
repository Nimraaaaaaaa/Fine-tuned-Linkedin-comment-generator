# 🚀 Fine-tuned LinkedIn Comment Generator

An AI-powered application that generates human-like, personalized LinkedIn comments using GPT-4o fine-tuned model. The app features Firebase authentication, user history tracking, and tone-based comment personalization deployed on Render.

## ✨ Features

- **🤖 GPT-4o Fine-tuned Model**: Custom fine-tuned GPT-4o for generating high-quality, contextually relevant LinkedIn comments
- **🔐 Firebase Authentication**: Secure user authentication with email/password and username
- **💾 User History Tracking**: All generated comments are saved to Firebase for future reference
- **🎨 Personalized Tone Selection**: Users can provide sample comments to train the model on their unique writing style
- **👤 Style Persistence**: Uses ChromaDB vector database to maintain and retrieve user-specific writing patterns
- **📊 Multi-Page Interface**: Interactive Streamlit application with dedicated sections for different functionalities
- **☁️ Cloud Deployed**: Live application deployed on Render for 24/7 accessibility
- **🔄 Real-time Generation**: Instant comment generation with user's preferred tone

## 🛠️ Tech Stack

- **Python 3.x**
- **Streamlit**: Web application framework
- **GPT-4o (Fine-tuned)**: OpenAI's GPT-4o model fine-tuned for better comment generation
- **Firebase**: 
  - Firebase Authentication (Email/Password)
  - Firestore Database (User history & preferences)
- **ChromaDB**: Vector database for storing user tone embeddings
- **LangChain**: For building LLM applications and RAG pipeline
- **Render**: Cloud platform for application deployment
- **Environment Variables**: Secure API key management

## 📁 Project Structure

```
Fine-tuned-Linkedin-comment-generator/
│
├── app_pages/                    # Streamlit multi-page app modules
│   ├── __init__.py
│   ├── authentication.py         # User login/signup page
│   ├── comment_generator.py      # Main comment generation interface
│   ├── history.py                # User comment history viewer
│   └── tone_trainer.py           # User tone preference section
│
├── .env                          # Environment variables (API keys, Firebase config)
├── app.py                        # Main Streamlit application entry point
├── chroma_style_dp.py            # ChromaDB style database operations
├── human_style_generator.py      # Human-like comment style generation with GPT-4o
├── load_and_embeded.py          # User tone loading and embedding creation
├── main.py                       # Core logic and orchestration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- OpenAI API key (with GPT-4o access)
- Firebase project credentials
- Render account (for deployment)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/Nimraaaaaaaa/Fine-tuned-Linkedin-comment-generator.git
cd Fine-tuned-Linkedin-comment-generator
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
GPT_MODEL=gpt-4o-finetuned-model-id

# Firebase Configuration
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_DATABASE_URL=your_database_url

# Render Configuration (for deployment)
RENDER_EXTERNAL_URL=your-app-url.onrender.com
```

### 2. Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable **Authentication** with Email/Password provider
3. Create a **Firestore Database** with these collections:
   - `users`: Store user profiles
   - `comment_history`: Store generated comments
   - `user_tones`: Store user tone preferences

### 3. ChromaDB Configuration

The application automatically creates a local ChromaDB instance for storing user tone embeddings.

## 🚀 Usage

### Running Locally

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Deployed Application

Access the live application at: `https://your-app-name.onrender.com`

## 📱 Application Workflow

### 1. **User Authentication**
- New users sign up with email, password, and username
- Existing users log in with their credentials
- Firebase handles secure authentication

### 2. **Tone Personalization** (Optional but Recommended)
- Navigate to the "Train Your Tone" section
- Provide 3-5 sample comments that reflect your writing style
- The model analyzes and stores your unique tone patterns in ChromaDB
- Your tone is associated with your user profile

### 3. **Generate Comments**
- Paste a LinkedIn post you want to comment on
- Select your preferred tone (or use your trained custom tone)
- Click "Generate Comment"
- The fine-tuned GPT-4o model creates a contextually relevant comment

### 4. **View History**
- Access your comment history from the sidebar
- All generated comments are saved with timestamps
- Review, copy, or regenerate previous comments

## 🧠 How It Works

### Architecture Overview

```
User Authentication (Firebase Auth)
        ↓
User Profile & Preferences (Firestore)
        ↓
Tone Training (Optional)
        ↓
Tone Embeddings (ChromaDB)
        ↓
LinkedIn Post Input
        ↓
Tone Retrieval + Context Building
        ↓
Fine-tuned GPT-4o Generation
        ↓
Comment Output + History Save (Firestore)
```

### Technical Flow

1. **Authentication Layer**: Firebase verifies user credentials and manages sessions
2. **Tone Analysis**: When users provide sample comments, the system:
   - Extracts linguistic patterns and style markers
   - Creates vector embeddings using text-embedding models
   - Stores embeddings in ChromaDB with user_id reference
3. **Generation Process**:
   - User submits LinkedIn post content
   - System retrieves user's tone embeddings from ChromaDB
   - Fine-tuned GPT-4o receives: post content + user tone context
   - Model generates comment matching user's style
4. **History Management**: Generated comment is saved to Firestore with:
   - User ID
   - Original post
   - Generated comment
   - Timestamp
   - Tone used

## 🎯 Key Features Explained

### Fine-tuned GPT-4o Model

Our GPT-4o model is specifically fine-tuned on thousands of LinkedIn comments to understand:
- Professional networking language
- Industry-specific terminology
- Engagement-driving comment patterns
- Natural conversation flow
- Appropriate emoji usage

### Tone Personalization

The system learns your unique writing style through:
- **Vocabulary preferences**: Words and phrases you commonly use
- **Sentence structure**: Your typical comment length and complexity
- **Engagement style**: Professional, casual, enthusiastic, analytical, etc.
- **Emoji usage**: Your pattern of using emojis and which ones

### Firebase Integration

**Authentication Benefits:**
- Secure user management
- Password reset functionality
- Email verification (optional)
- Multi-device access with same account

**History Storage Benefits:**
- Persistent comment history across sessions
- Search and filter previous comments
- Track usage patterns
- Export comment history

## 🚢 Deployment on Render

The application is deployed on Render with the following configuration:

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `streamlit run app.py --server.port=$PORT`
3. **Environment Variables**: All Firebase and OpenAI credentials configured in Render dashboard
4. **Auto-deploy**: Enabled for main branch updates

**Live URL**: Your deployed app is accessible 24/7 at the Render URL

## 🔒 Security Best Practices

- Never commit `.env` file to version control
- Firebase credentials are environment variables only
- User passwords are hashed by Firebase Authentication
- API keys are stored securely in Render's environment variables
- ChromaDB data is isolated per user

## 📊 Example Usage

```python
# After authentication and tone training

Post Input: 
"Just launched our new AI-powered analytics platform! 
Check it out at example.com"

User's Tone Profile: 
- Professional yet enthusiastic
- Uses data-driven language
- Occasional emojis

Generated Comment:
"Congratulations on the launch! 🎉 The AI-powered analytics 
capabilities look impressive. I'm particularly interested in 
how you're handling real-time data processing. Would love to 
see a demo of the dashboard features. Best of luck with the 
rollout!"
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to all functions
- Test Firebase integration locally before committing
- Update documentation for new features
- Ensure environment variables are properly documented

## 📝 Roadmap

- [ ] Add support for multiple languages
- [ ] Implement LinkedIn post analyzer for better context
- [ ] Create browser extension for one-click commenting
- [ ] Add team collaboration features
- [ ] Integrate sentiment analysis for comment tone adjustment
- [ ] Add analytics dashboard for tracking comment engagement
- [ ] Support for other social platforms (Twitter, Facebook)

## 🐛 Troubleshooting

**Firebase Connection Issues:**
- Verify your Firebase credentials in `.env`
- Check Firestore security rules
- Ensure Authentication is enabled in Firebase Console

**GPT-4o API Errors:**
- Confirm your OpenAI API key has GPT-4o access
- Check your API usage limits
- Verify the fine-tuned model ID is correct

**ChromaDB Errors:**
- Delete `chroma_db` folder and restart the app
- Ensure sufficient disk space for embeddings

## ⚠️ Disclaimer

This tool is designed to assist with LinkedIn engagement by generating comment suggestions. Users are responsible for:
- Reviewing generated comments before posting
- Ensuring comments align with LinkedIn's Terms of Service
- Using the tool ethically and responsibly
- Not spamming or automated posting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o and fine-tuning capabilities
- Firebase for authentication and database services
- ChromaDB for vector database functionality
- Streamlit for the intuitive web framework
- Render for reliable cloud hosting
- The open-source community

## 📧 Contact

**Nimra** - [@Nimraaaaaaaa](https://github.com/Nimraaaaaaaa)

Project Link: [https://github.com/Nimraaaaaaaa/Fine-tuned-Linkedin-comment-generator](https://github.com/Nimraaaaaaaa/Fine-tuned-Linkedin-comment-generator)

**Live Application**: [https://ahadd-frontend.onrender.com]

---

⭐ **Found this helpful? Give it a star and share with your network!**

🚀 **Happy Commenting! Let AI enhance your LinkedIn presence.**
