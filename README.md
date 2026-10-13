# 🎀 StyleMe — AI-Powered Wardrobe Assistant

StyleMe is a fashion recommendation web application that helps users organise their wardrobe and discover outfit combinations based on their personal style, occasion, and local weather.

## ✨ Features

* **AI clothing recognition:** Analyse uploaded clothing photos using a machine-learning model.
* **Editable predictions:** Review and correct the predicted clothing details before saving.
* **Digital wardrobe:** Store clothing items, colours, categories, styles, and photos.
* **Weather-aware recommendations:** Use local weather information to help choose suitable outfits.
* **Personalised outfit generation:** Generate combinations based on style and occasion.
* **AI outfit explanations:** Receive a natural-language explanation of why an outfit works.
* **Outfit variety:** Generate alternative combinations.
* **Wardrobe management:** View and remove saved clothing items.

## 🛠️ Technologies

* Python
* Flask
* SQLite
* PyTorch
* Hugging Face Transformers
* Hugging Face Inference API
* Pillow
* HTML, CSS, and JavaScript
* Open-Meteo weather API
* `unittest` for automated testing

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd StyleMe
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository's clone URL.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your environment variables

Create a `.env` file in the project root:

```text
HF_TOKEN=your_hugging_face_token
```

Get a token from [Hugging Face](https://huggingface.co/settings/tokens) if you want to use the hosted AI outfit explanations.

**Never commit your real `.env` file or API token.** The application includes a fallback explanation when a token isn't configured.

### 5. Run the application

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The SQLite database is initialised automatically. The clothing-recognition model may need to download the first time it is used.

## 🧪 Run the tests

```bash
python -m unittest discover -s tests -v
```

## 🔒 Security and privacy

Environment secrets, the local SQLite database, uploaded clothing photos, and virtual environments should remain outside version control.

## 👗 Project Goals

StyleMe was developed as a computer science portfolio project to explore web development, object-oriented programming, database management, machine learning integration, and personalised recommendation systems.

---

*Built with Python and a love of fashion 💗*
