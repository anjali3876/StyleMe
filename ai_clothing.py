from transformers import pipeline
from PIL import Image


# Fashion-specific AI model
classifier = pipeline(
    "image-classification",
    model="dima806/clothes_image_detection"
)


def detect_colour(image_path):
    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    # Focus on the centre of the image
    left = width * 0.2
    top = height * 0.2
    right = width * 0.8
    bottom = height * 0.8

    image = image.crop((left, top, right, bottom))
    image = image.resize((50, 50))

    pixels = list(image.getdata())

    average_colour = tuple(
        sum(pixel[i] for pixel in pixels) // len(pixels)
        for i in range(3)
    )

    red, green, blue = average_colour

    if red < 60 and green < 60 and blue < 60:
        return "Black"

    if red > 200 and green > 200 and blue > 200:
        return "White"

    if blue > red * 1.15 and blue > green * 1.05:
        return "Blue"

    if green > red * 1.15 and green > blue * 1.05:
        return "Green"

    if red > green * 1.25 and red > blue * 1.25:
        return "Red"

    if red > 150 and blue > 100 and green < 170:
        return "Pink"

    if red > 150 and green > 130 and blue < 120:
        return "Yellow"

    if abs(red - green) < 20 and abs(green - blue) < 20:
        return "Neutral"

    return "Other"
if __name__ == "__main__":
    image_path = "uploads/clothing_3.png"

    results = classifier(image_path)

    print("\n🤖 AI CLOTHING RESULTS:\n")

    for result in results[:5]:
        print(
            result["label"],
            "-",
            round(result["score"] * 100, 2),
            "%"
        )

    colour = detect_colour(image_path)

    print("\n🎨 DETECTED COLOUR:")
    print(colour)