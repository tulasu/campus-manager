"""Dependency injection for Google Sheets client."""

from typing import Annotated

from fastapi import Request, Depends
import gspread

from core.logging import get_logger

logger = get_logger(__name__)


def get_gspread_spreadsheet(request: Request) -> gspread.Spreadsheet:
    """Get Google Sheets client from application state."""
    try:
        return request.app.state.spreadsheet
    except AttributeError:
        logger.error("Google Sheets client not initialized in application state")
        raise RuntimeError("Google Sheets client not available. Check application startup.")


GspreadDep = Annotated[gspread.Spreadsheet, Depends(get_gspread_spreadsheet)]
