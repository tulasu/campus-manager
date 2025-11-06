"""Application lifespan management for Campus Manager."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from google.oauth2.service_account import Credentials
import gspread

from core.config import settings
from core.db import create_db_and_tables
from core.exceptions import ConfigurationError
from core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    try:
        logger.info("Starting up Campus Manager application")

        # Initialize database
        logger.info("Initializing database tables")
        create_db_and_tables()

        # Initialize Google Sheets client
        logger.info("Initializing Google Sheets client")
        try:
            credentials = Credentials.from_service_account_file(
                settings.google_service_account,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_key(settings.google_sheet_id)
            app.state.spreadsheet = spreadsheet
            logger.info(f"Successfully connected to Google Sheets: {spreadsheet.title}")

        except FileNotFoundError:
            raise ConfigurationError(
                f"Service account file not found: {settings.google_service_account}"
            )
        except gspread.exceptions.SpreadsheetNotFound:
            raise ConfigurationError(
                f"Google Sheet not found with ID: {settings.google_sheet_id}"
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to connect to Google Sheets: {str(e)}")

        logger.info("Campus Manager application startup complete")
        yield

    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise

    finally:
        logger.info("Campus Manager application shutting down")
