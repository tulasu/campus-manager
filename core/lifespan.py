from contextlib import asynccontextmanager

from fastapi import FastAPI
from google.oauth2.service_account import Credentials
import gspread

from core.config import config
from core.db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    creds = Credentials.from_service_account_file(
        config.google_service_account,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    spreadsheet = gspread.authorize(creds).open_by_key(config.google_sheet_id)
    app.state.spreadsheet = spreadsheet
    yield
