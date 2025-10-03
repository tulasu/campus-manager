from typing import Annotated

from fastapi import Request, Depends
import gspread


def get_gspread_spreadsheet(request: Request) -> gspread.Spreadsheet:
    return request.app.state.spreadsheet


GspreadDep = Annotated[gspread.Spreadsheet, Depends(get_gspread_spreadsheet)]
