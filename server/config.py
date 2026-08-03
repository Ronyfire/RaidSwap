import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    # No refresh token yet (see my-coding-patterns JWT section) — 3h keeps a
    # tester's session alive through a normal raid without forcing re-login
    # mid-session. Revisit down when a refresh-token flow lands.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)
