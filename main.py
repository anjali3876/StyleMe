import requests
from itertools import product

from database import get_all_clothing


# -------------------------
# CLOTHING ITEM
# -------------------------

class ClothingItem:
    def __init__(self, name, category, colour, style, photo=None):
        self.name = name
        self.category = category
        self.colour = colour
        self.style = style
        self.photo = photo


# -------------------------
# LOAD WARDROBE
# -------------------------

def load_wardrobe():
    clothing_data = get_all_clothing()
    wardrobe = []

    for item in clothing_data:
        wardrobe.append(
            ClothingItem(
                item[1],
                item[2],
                item[3],
                item[4],
                item[5]
            )
        )

    return wardrobe


# -------------------------
# STYLE RULES
# -------------------------

compatible_styles = {
    "Feminine": ["Feminine", "Preppy", "Casual"],
    "Casual": ["Casual", "Feminine"],
    "Preppy": ["Preppy", "Feminine", "Casual"],
    "Y2K": ["Y2K", "Casual", "Feminine"],
    "Minimalist": ["Minimalist", "Casual", "Preppy"]
}


occasion_styles = {
    "Uni": ["Casual", "Feminine", "Preppy"],
    "Casual": ["Casual", "Feminine"],
    "Date": ["Feminine", "Preppy"],
    "Going out": ["Feminine", "Y2K"],
    "Party": ["Feminine", "Y2K", "Preppy"]
}


# -------------------------
# WEATHER STYLE RULES
# -------------------------

weather_rules = {
    "Warm": ["Feminine", "Casual", "Preppy"],
    "Cold": ["Casual", "Preppy"],
    "Rainy": ["Casual", "Preppy"],
    "Sunny": ["Feminine", "Casual", "Preppy"]
}


# -------------------------
# COLOUR RULES
# -------------------------

colour_pairs = {
    "Black": ["White", "Pink", "Blue", "Black", "Neutral"],
    "White": ["Black", "Pink", "Blue", "White", "Neutral"],
    "Pink": ["Black", "White", "Blue", "Pink", "Neutral"],
    "Blue": ["White", "Black", "Pink", "Blue", "Neutral"],
    "Neutral": ["Black", "White", "Pink", "Blue", "Neutral"]
}


def colours_match(first_colour, second_colour):

    first_colour = first_colour.title()
    second_colour = second_colour.title()

    if first_colour == second_colour:
        return True

    if first_colour in colour_pairs:
        return second_colour in colour_pairs[first_colour]

    return False


# -------------------------
# WEATHER FUNCTION
# -------------------------

def get_weather(city):

    location_url = "https://geocoding-api.open-meteo.com/v1/search"

    location_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    location_response = requests.get(
        location_url,
        params=location_params
    )

    location_data = location_response.json()

    if "results" not in location_data:
        return None

    latitude = location_data["results"][0]["latitude"]
    longitude = location_data["results"][0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code"
    }

    weather_response = requests.get(
        weather_url,
        params=weather_params
    )

    weather_data = weather_response.json()

    temperature = weather_data["current"]["temperature_2m"]
    weather_code = weather_data["current"]["weather_code"]

    if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        weather_type = "Rainy"

    elif temperature >= 18:
        weather_type = "Warm"

    elif temperature <= 10:
        weather_type = "Cold"

    else:
        weather_type = "Sunny"

    return {
        "temperature": temperature,
        "weather_type": weather_type
    }


# -------------------------
# WEATHER CLOTHING SCORE
# -------------------------

def weather_clothing_score(item, weather_type):

    name = item.name.lower()
    category = item.category.lower()

    score = 0

    # -------------------------
    # COLD WEATHER
    # -------------------------

    if weather_type == "Cold":

        if "cardigan" in name:
            score += 6

        if "jacket" in name:
            score += 6

        if "hoodie" in name:
            score += 5

        if "coat" in name:
            score += 6

        if "jeans" in name:
            score += 4

        if "trousers" in name:
            score += 4

        if category == "bottom":
            score += 1

        if category == "top":
            score += 1


    # -------------------------
    # WARM WEATHER
    # -------------------------

    elif weather_type == "Warm":

        if "skirt" in name:
            score += 5

        if "shorts" in name:
            score += 6

        if "baby tee" in name:
            score += 5

        if "fitted top" in name:
            score += 4

        if category == "top":
            score += 2


    # -------------------------
    # RAINY WEATHER
    # -------------------------

    elif weather_type == "Rainy":

        if "jeans" in name:
            score += 5

        if "trousers" in name:
            score += 5

        if "hoodie" in name:
            score += 4

        if "jacket" in name:
            score += 6

        if category == "bottom":
            score += 2

        if category == "shoes":
            score += 1


    # -------------------------
    # SUNNY WEATHER
    # -------------------------

    elif weather_type == "Sunny":

        if "skirt" in name:
            score += 5

        if "shorts" in name:
            score += 6

        if "baby tee" in name:
            score += 4

        if "fitted top" in name:
            score += 3

        if category == "top":
            score += 2


    return score


# -------------------------
# OUTFIT SCORING
# -------------------------

def score_outfit(
    top,
    bottom,
    shoes,
    user_style,
    user_occasion,
    weather_type
):

    score = 0

    # -------------------------
    # STYLE SCORE
    # -------------------------

    preferred_styles = compatible_styles.get(
        user_style,
        [user_style]
    )

    for item in [top, bottom, shoes]:

        if item.style == user_style:
            score += 4

        elif item.style in preferred_styles:
            score += 2


    # -------------------------
    # OCCASION SCORE
    # -------------------------

    occasion_preferences = occasion_styles.get(
        user_occasion,
        []
    )

    for item in [top, bottom, shoes]:

        if item.style in occasion_preferences:
            score += 2


    # -------------------------
    # WEATHER STYLE SCORE
    # -------------------------

    weather_preferences = weather_rules.get(
        weather_type,
        []
    )

    for item in [top, bottom, shoes]:

        if item.style in weather_preferences:
            score += 1


    # -------------------------
    # ACTUAL WEATHER SCORE
    # -------------------------

    score += weather_clothing_score(top, weather_type)
    score += weather_clothing_score(bottom, weather_type)
    score += weather_clothing_score(shoes, weather_type)


    # -------------------------
    # COLOUR SCORE
    # -------------------------

    if colours_match(top.colour, bottom.colour):
        score += 3

    if colours_match(bottom.colour, shoes.colour):
        score += 2


    # -------------------------
    # PHOTO SCORE
    # -------------------------

    for item in [top, bottom, shoes]:

        if item.photo:
            score += 1


    return score


# -------------------------
# OUTFIT GENERATOR
# -------------------------

def generate_outfit(
    user_style,
    user_occasion,
    weather_type=None,
    avoid_outfit=None
):

    wardrobe = load_wardrobe()

    allowed_styles = compatible_styles.get(
        user_style,
        [user_style]
    )

    # Match the occasion
    if user_occasion in occasion_styles:

        allowed_styles = list(
            set(allowed_styles)
            & set(occasion_styles[user_occasion])
        )

    # Match the weather
    if weather_type in weather_rules:

        allowed_styles = list(
            set(allowed_styles)
            & set(weather_rules[weather_type])
        )


    # -------------------------
    # FILTER WARDROBE
    # -------------------------

    style_tops = []
    style_bottoms = []
    style_shoes = []

    for item in wardrobe:

        if item.style in allowed_styles:

            if item.category == "Top":
                style_tops.append(item)

            elif item.category == "Bottom":
                style_bottoms.append(item)

            elif item.category == "Shoes":
                style_shoes.append(item)


    # -------------------------
    # CHECK CLOTHING
    # -------------------------

    if not style_tops:
        return None

    if not style_bottoms:
        return None

    if not style_shoes:
        return None


    # -------------------------
    # CREATE POSSIBLE OUTFITS
    # -------------------------

    possible_outfits = list(
        product(
            style_tops,
            style_bottoms,
            style_shoes
        )
    )


    # -------------------------
    # SCORE EACH OUTFIT
    # -------------------------

    scored_outfits = []

    for top, bottom, shoes in possible_outfits:

        score = score_outfit(
            top,
            bottom,
            shoes,
            user_style,
            user_occasion,
            weather_type
        )

        scored_outfits.append(
            (
                score,
                top,
                bottom,
                shoes
            )
        )


    # -------------------------
    # SORT BY BEST SCORE
    # -------------------------

    scored_outfits.sort(
        key=lambda outfit: outfit[0],
        reverse=True
    )


    # -------------------------
    # -------------------------
# ENCOURAGE OUTFIT VARIETY
# -------------------------

    # -------------------------
    # ENCOURAGE OUTFIT VARIETY
    # -------------------------

    if avoid_outfit:

        varied_outfits = []

        for outfit in scored_outfits:

            score, top, bottom, shoes = outfit

            outfit_names = (
                top.name,
                bottom.name,
                shoes.name
            )

            if outfit_names == tuple(avoid_outfit):
                continue

            variety_bonus = 0

            # Reward changing the top
            if top.name != avoid_outfit[0]:
                variety_bonus += 3

            # Reward changing the bottom
            if bottom.name != avoid_outfit[1]:
                variety_bonus += 3

            # Reward changing the shoes
            if shoes.name != avoid_outfit[2]:
                variety_bonus += 2

            varied_outfits.append(
                (
                    score + variety_bonus,
                    top,
                    bottom,
                    shoes
                )
            )

        if varied_outfits:

            scored_outfits = varied_outfits

            scored_outfits.sort(
                key=lambda outfit: outfit[0],
                reverse=True
            )


    # -------------------------
    # CHOOSE FROM TOP OUTFITS
    # -------------------------

    top_outfits = scored_outfits[:5]

    chosen_score, chosen_top, chosen_bottom, chosen_shoes = (
        top_outfits[0]
    )

    return (
        chosen_top,
        chosen_bottom,
        chosen_shoes
    )

