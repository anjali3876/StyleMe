
import os
import sqlite3
import uuid
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
)
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from main import generate_outfit, get_weather
from database import add_clothing, get_all_clothing
from ai_clothing import classifier, detect_colour
from llm_explanation import generate_outfit_explanation


app = Flask(__name__)

BASE_DIR = Path(app.root_path)
UPLOAD_FOLDER = BASE_DIR / "uploads"
DATABASE_PATH = BASE_DIR / "styleme.db"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

ALLOWED_STYLES = {
    "Feminine", "Casual", "Preppy", "Y2K", "Minimalist"
}

ALLOWED_OCCASIONS = {
    "Uni", "Date", "Party", "Casual", "Going out"
}

ALLOWED_CATEGORIES = {"Top", "Bottom", "Shoes"}


def error_page(message, status=400):
    return (
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>StyleMe 🎀</title>
            <link rel="stylesheet"
                  href="{url_for('static', filename='style.css')}">
        </head>
        <body>
            <div class="outfit-card">
                <h1>🎀 StyleMe</h1>
                <p>{message}</p>
                <a href="/" class="back-button">← Back to StyleMe</a>
            </div>
        </body>
        </html>
        """,
        status,
    )


def fetch_weather(city):
    if not city or not city.strip():
        return None

    try:
        return get_weather(city.strip())
    except Exception:
        app.logger.exception("Weather lookup failed")
        return None


def explain_outfit(
    top, bottom, shoes, style, occasion, weather_type, temperature
):
    try:
        explanation = generate_outfit_explanation(
            top,
            bottom,
            shoes,
            style,
            occasion,
            weather_type,
            temperature,
        )

        return explanation or "A look selected from your wardrobe."

    except Exception:
        app.logger.exception("Outfit explanation failed")
        return "Your outfit has been selected from your wardrobe."


def render_generated_outfit(style, occasion, city, weather, outfit):
    top, bottom, shoes = outfit

    explanation = explain_outfit(
        top,
        bottom,
        shoes,
        style,
        occasion,
        weather["weather_type"],
        weather["temperature"],
    )

    return render_template(
        "outfit.html",
        style=style,
        occasion=occasion,
        city=city,
        temperature=weather["temperature"],
        weather_type=weather["weather_type"],
        outfit=outfit,
        explanation=explanation,
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    user_style = request.form.get("style", "")
    user_occasion = request.form.get("occasion", "")
    city = request.form.get("city", "").strip()

    if user_style not in ALLOWED_STYLES:
        return error_page("Please choose a valid style.")

    if user_occasion not in ALLOWED_OCCASIONS:
        return error_page("Please choose a valid occasion.")

    if not city:
        return error_page("Please enter a city.")

    weather = fetch_weather(city)

    if weather is None:
        return error_page(
            "We couldn't find that city or retrieve its weather. "
            "Please check the city and try again."
        )

    try:
        outfit = generate_outfit(
            user_style,
            user_occasion,
            weather["weather_type"],
        )
    except Exception:
        app.logger.exception("Outfit generation failed")
        return error_page(
            "Something went wrong while creating your outfit.",
            500,
        )

    if not outfit:
        return error_page(
            "There aren't enough suitable clothes in your wardrobe "
            "for this combination yet."
        )

    return render_generated_outfit(
        user_style, user_occasion, city, weather, outfit
    )


@app.route("/generate-another", methods=["POST"])
def generate_another():
    user_style = request.form.get("style", "")
    user_occasion = request.form.get("occasion", "")
    city = request.form.get("city", "").strip()

    if user_style not in ALLOWED_STYLES:
        return error_page("Please choose a valid style.")

    if user_occasion not in ALLOWED_OCCASIONS:
        return error_page("Please choose a valid occasion.")

    if not city:
        return error_page("Please enter a city.")

    current_outfit = (
        request.form.get("current_top", ""),
        request.form.get("current_bottom", ""),
        request.form.get("current_shoes", ""),
    )

    weather = fetch_weather(city)

    if weather is None:
        return error_page(
            "We couldn't retrieve the weather. Please try again."
        )

    try:
        outfit = generate_outfit(
            user_style,
            user_occasion,
            weather["weather_type"],
            avoid_outfit=current_outfit,
        )
    except Exception:
        app.logger.exception("Alternative outfit generation failed")
        return error_page("We couldn't generate another outfit.", 500)

    if not outfit:
        return error_page(
            "There aren't enough suitable clothes for another outfit yet."
        )

    return render_generated_outfit(
        user_style, user_occasion, city, weather, outfit
    )


@app.route("/add-clothing", methods=["POST"])
def add_clothing_item():
    photo = request.files.get("photo")

    if not photo or not photo.filename:
        return error_page("Please select a clothing photo.")

    safe_original_name = secure_filename(photo.filename)
    extension = Path(safe_original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return error_page(
            "Please upload a JPG, JPEG, PNG or WEBP image."
        )

    # Generate a unique filename to avoid overwriting other uploads.
    filename = f"{uuid.uuid4().hex}{extension}"
    photo_path = UPLOAD_FOLDER / filename

    try:
        photo.save(str(photo_path))

        # Check that the uploaded file is a genuine, readable image.
        with Image.open(photo_path) as image:
            image.verify()

        # Run the AI model on the validated image.
        results = classifier(str(photo_path))

        if not results:
            raise ValueError("The model returned no predictions.")

        predictions = [
            {
                "label": result["label"],
                "confidence": round(result["score"] * 100, 2),
            }
            for result in results[:5]
        ]

        ai_prediction = predictions[0]["label"]
        detected_colour = detect_colour(str(photo_path))

    except (UnidentifiedImageError, OSError, ValueError):
        photo_path.unlink(missing_ok=True)
        return error_page("That image could not be read. Try another photo.")

    except Exception:
        photo_path.unlink(missing_ok=True)
        app.logger.exception("Clothing image analysis failed")
        return error_page(
            "The clothing analyser couldn't process that image. "
            "Please try again.",
            500,
        )

    # Map common model labels to wardrobe categories.
    label = ai_prediction.lower()

    shoe_keywords = (
        "shoe", "sneaker", "trainer", "boot", "loafer",
        "sandal", "heel", "ballet flat", "footwear",
    )
    bottom_keywords = (
        "jeans", "trouser", "pants", "shorts", "skirt",
        "legging",
    )

    if any(word in label for word in shoe_keywords):
        category = "Shoes"
    elif any(word in label for word in bottom_keywords):
        category = "Bottom"
    else:
        category = "Top"

    if "skirt" in label:
        suggested_style = "Feminine"
    elif any(word in label for word in (
        "jeans", "trouser", "pants", "shorts", "sneaker", "trainer"
    )):
        suggested_style = "Casual"
    else:
        suggested_style = "Feminine"

    return render_template(
        "ai_result.html",
        prediction=ai_prediction,
        confidence=predictions[0]["confidence"],
        photo=filename,
        name=ai_prediction,
        category=category,
        colour=detected_colour,
        style=suggested_style,
        predictions=predictions,
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    # Never allow a path supplied by the URL to escape uploads/.
    safe_name = secure_filename(filename)

    if not safe_name or safe_name != filename:
        return error_page("Invalid photo filename.", 404)

    return send_from_directory(str(UPLOAD_FOLDER), safe_name)


@app.route("/confirm-clothing", methods=["POST"])
def confirm_clothing():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "")
    colour = request.form.get("colour", "").strip()
    style = request.form.get("style", "")
    photo = request.form.get("photo", "")

    if not name or len(name) > 100:
        return error_page("Please enter a valid clothing item name.")

    if not colour or len(colour) > 50:
        return error_page("Please enter a valid colour.")

    if category not in ALLOWED_CATEGORIES:
        return error_page("Please select a valid clothing category.")

    if style not in ALLOWED_STYLES:
        return error_page("Please select a valid style.")

    # Only accept filenames of images already stored in uploads/.
    if (
        not photo
        or secure_filename(photo) != photo
        or not (UPLOAD_FOLDER / photo).is_file()
    ):
        return error_page(
            "The clothing photo is missing. Please upload it again."
        )

    try:
        add_clothing(name, category, colour, style, photo)
    except Exception:
        app.logger.exception("Saving clothing failed")
        return error_page("We couldn't save this item.", 500)

    return redirect(url_for("wardrobe_page"))


@app.route("/wardrobe")
def wardrobe_page():
    clothing = get_all_clothing()

    return render_template(
        "wardrobe.html",
        clothing=clothing,
    )


@app.route("/delete-clothing/<int:item_id>", methods=["POST"])
def delete_clothing(item_id):
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT photo FROM clothing WHERE id = ?",
            (item_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return error_page("That wardrobe item wasn't found.", 404)

        cursor.execute(
            "DELETE FROM clothing WHERE id = ?",
            (item_id,),
        )
        connection.commit()

        # Remove the image only if it is a valid local upload filename.
        photo = row[0]

        if photo and secure_filename(photo) == photo:
            photo_path = UPLOAD_FOLDER / photo

            if photo_path.is_file():
                photo_path.unlink()

    except Exception:
        connection.rollback()
        app.logger.exception("Deleting clothing failed")
        return error_page("We couldn't remove this item.", 500)

    finally:
        connection.close()

    return redirect(url_for("wardrobe_page"))


@app.errorhandler(413)
def file_too_large(error):
    return error_page(
        "That photo is too large. Please choose an image under 8 MB.",
        413,
    )


if __name__ == "__main__":
    app.run(debug=True)