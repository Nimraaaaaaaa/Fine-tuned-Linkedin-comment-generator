# 🚀 Fine-tuned LinkedIn Comment Generator

An AI-powered application that generates human-like, personalized LinkedIn comments using fine-tuned language models and RAG (Retrieval-Augmented Generation) techniques with ChromaDB for style persistence.

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Fine-tuned AI Models**: Leverages custom-trained models for generating contextually relevant LinkedIn comments
- **Human-Style Generation**: Creates comments that mimic natural human writing patterns
- **Style Persistence**: Uses ChromaDB vector database to maintain consistent writing styles
- **Multi-Page App Interface**: Interactive Streamlit application with multiple pages for different functionalities
- **Embedding-Based Retrieval**: Employs semantic search to find and apply appropriate comment styles
- **Customizable Output**: Generate comments tailored to different post types and tones

## 🛠️ Tech Stack

- **Python 3.x**
- **Streamlit**: Web application framework
- **ChromaDB**: Vector database for style embeddings
- **LangChain**: For building LLM applications
- **OpenAI API / HuggingFace**: Language model integration
- **Environment Variables**: Secure API key management

## 📁 Project Structure

```
Fine-tuned-Linkedin-comment-generator/
│
├── app_pages/                    # Streamlit multi-page app modules
│   ├── __init__.py
│   └── [page modules]
│
├── .env                          # Environment variables (API keys, configs)
├── app.py                        # Main Streamlit application entry point
├── chroma_style_dp.py            # ChromaDB style database operations
├── human_style_generator.py      # Human-like comment style generation
├── load_and_embeded.py          # Data loading and embedding creation
├── main.py                       # Core logic and orchestration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- API keys (OpenAI/HuggingFace)

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

1. **Create a `.env` file** in the root directory with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here
# Add other environment variables as needed
```

2. **Configure ChromaDB** (if needed):
   - The application will automatically create a local ChromaDB instance
   - Custom configurations can be modified in `chroma_style_dp.py`

## 🚀 Usage

### Running the Application

**Option 1: Streamlit App (Recommended)**
```bash
streamlit run app.py
```

**Option 2: Main Script**
```bash
python main.py
```

### Using the Application

1. **Launch the app** and navigate through different pages
2. **Input a LinkedIn post** or select a post type
3. **Choose comment style** (professional, casual, insightful, etc.)
4. **Generate comment** using the AI model
5. **Copy and use** the generated comment on LinkedIn

### Example

```python
# Quick example of generating a comment
from human_style_generator import generate_comment

post_content = "Just launched our new AI product!"
comment = generate_comment(post_content, style="professional")
print(comment)
# Output: "Congratulations on the launch! The AI capabilities look impressive. 
# Would love to learn more about the technology stack behind it. 🚀"
```

## 🧠 How It Works

1. **Data Loading**: Historical LinkedIn comments and styles are loaded via `load_and_embeded.py`
2. **Embedding Creation**: Comments are converted to vector embeddings for semantic search
3. **Style Database**: ChromaDB stores and retrieves similar comment styles
4. **Generation**: Fine-tuned model generates comments using retrieved context
5. **Human-like Output**: Post-processing ensures natural, engaging output

### Architecture Flow

```
User Input → Style Retrieval (ChromaDB) → Context Building → 
LLM Generation → Style Post-processing → Final Comment
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide for Python code
- Add docstrings to all functions
- Update documentation for new features
- Test your changes thoroughly

## 📝 TODO / Roadmap

- [ ] Add support for multiple languages
- [ ] Implement comment tone analyzer
- [ ] Create browser extension for one-click commenting
- [ ] Add A/B testing for different comment styles
- [ ] Integrate with LinkedIn API (if available)
- [ ] Add analytics dashboard

## ⚠️ Disclaimer

This tool is designed to assist with LinkedIn engagement. Please use responsibly and in accordance with LinkedIn's Terms of Service. Automated posting and commenting may violate LinkedIn's policies if not used appropriately.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Acknowledgments

- OpenAI for GPT models
- ChromaDB for vector database capabilities
- Streamlit for the amazing web framework
- The open-source community

## 📧 Contact


**Nimra** - [@Nimraaaaaaaa](https://github.com/Nimraaaaaaaa)

Project Link: [https://github.com/Nimraaaaaaaa/Fine-tuned-Linkedin-comment-generator](https://github.com/Nimraaaaaaaa/Fine-tuned-Linkedin-comment-generator)

---

⭐ If you find this project helpful, please consider giving it a star!
