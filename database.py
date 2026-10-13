
import sqlite3
from pathlib import Path


# Keep the database in the project folder, regardless of
# which directory the application is launched from.
DATABASE_PATH = Path(__file__).resolve().parent / "styleme.db"


def create_database():
    """Create the wardrobe table and migrate older databases."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clothing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                colour TEXT NOT NULL,
                style TEXT NOT NULL,
                photo TEXT
            )
        """)

        # Add the photo column to older databases if necessary.
        cursor.execute("PRAGMA table_info(clothing)")
        columns = [column[1] for column in cursor.fetchall()]

        if "photo" not in columns:
            cursor.execute(
                "ALTER TABLE clothing ADD COLUMN photo TEXT"
            )


def add_clothing(name, category, colour, style, photo=None):
    """Save one clothing item to the wardrobe."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            INSERT INTO clothing (name, category, colour, style, photo)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, colour, style, photo))


def get_all_clothing():
    """Return all wardrobe items, including their database IDs."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute("""
            SELECT id, name, category, colour, style, photo
            FROM clothing
            ORDER BY id
        """)

        return cursor.fetchall()


def delete_clothing_by_id(item_id):
    """Delete a wardrobe item by its database ID."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            "DELETE FROM clothing WHERE id = ?",
            (item_id,)
        )

        return cursor.rowcount > 0


# Initialise the database automatically when this module is imported.
# CREATE TABLE IF NOT EXISTS preserves existing wardrobe records.
create_database()