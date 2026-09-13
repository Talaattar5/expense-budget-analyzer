from sqlalchemy import insert, select

from app.database import engine
from app.models import categories

default_categories = [
    {"category_name": "Food"},
    {"category_name": "Transportation"},
    {"category_name": "Shopping"},
    {"category_name": "Education"},
    {"category_name": "Entertainment"},
    {"category_name": "Bills"},
    {"category_name": "Other"},
]


with engine.begin() as conn:
    existing = conn.execute(select(categories)).fetchall()

    if not existing:
        conn.execute(insert(categories), default_categories)
        print("Categories inserted successfully.")
    else:
        print("Categories already exist.")
