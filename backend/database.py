import os
import sqlite3
from datetime import datetime


DATA_FOLDER = "data"
DATABASE_FILE = os.path.join(DATA_FOLDER, "app.db")

os.makedirs(DATA_FOLDER, exist_ok=True)


def initialize_database():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prompt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            character_prompt TEXT NOT NULL,
            art_style TEXT NOT NULL,
            environment TEXT NOT NULL,
            enhancement TEXT NOT NULL,
            reference_instruction TEXT,
            reference_image_path TEXT,
            generated_image_path TEXT,
            image_status TEXT,
            final_prompt TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def save_prompt_history(request):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO prompt_history (
            created_at,
            character_prompt,
            art_style,
            environment,
            enhancement,
            reference_instruction,
            reference_image_path,
            generated_image_path,
            image_status,
            final_prompt
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            request.character_prompt,
            request.art_style,
            request.environment,
            request.enhancement,
            request.reference_instruction,
            request.reference_image_path,
            request.generated_image_path,
            request.image_status,
            request.final_prompt
        )
    )

    connection.commit()
    connection.close()


def get_prompt_history(limit=10):
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            created_at,
            character_prompt,
            art_style,
            environment,
            enhancement,
            reference_instruction,
            reference_image_path,
            generated_image_path,
            image_status,
            final_prompt
        FROM prompt_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def clear_prompt_history():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM prompt_history")

    connection.commit()
    connection.close()


def delete_prompt_history_item(history_id):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM prompt_history WHERE id = ?",
        (history_id,)
    )

    connection.commit()
    deleted_count = cursor.rowcount
    connection.close()

    return deleted_count