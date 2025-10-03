# Campus Manager

A streamlined application for students to submit housing applications and for administrators to manage room assignments.

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Architecture / Modules](#architecture--modules)  
4. [Setup & Installation](#setup--installation)  
5. [Running the Application](#running-the-application)  
6. [Google Sheets & Google Forms Integration](#google-sheets--google-forms-integration)  
7. [Creating Your Own Spreadsheet & Service Account Credentials](#creating-your-own-spreadsheet--service-account-credentials)
8. [License](#license)  

---

## Overview

Campus Manager is intended to facilitate the workflow of student housing applications. Students fill in a form (Google Form), submitting their details. Administrators view and manage assignments via a Google Spreadsheet (the “main table”) or via the app.

The project bridges between the Google Form responses, the Google Sheets API, and your own logic (Python backend) to process, display, and manage data.

Provided references:

- **Main table (Google Sheets)**:  
  <https://docs.google.com/spreadsheets/d/1Gmn0YiKvs_VG9nLmLl25eGTwCvgL494r7F6QUVcI03Q>  
- **Google Form used for submissions**:  
  <https://forms.gle/Mvdqyecxv7N1BRz58>  

---

## Features

- Accepts student submissions via a Google Form  
- Stores / synchronizes data into a Google Spreadsheet  
- Administrative interface (via backend logic) to assign rooms, manage statuses  
- Modular separation: domain logic, repositories (data access), service layer, handlers (HTTP endpoints)  
- Easy to adapt / extend (new fields, new workflows)  

---

## Architecture / Modules

Here's a rough breakdown of the directory structure / modules (as seen in the GitHub repo):

```

.
├── core
│   ├── config.py
│   ├── db.py
│   ├── __init__.py
│   ├── lifespan.py
│   └── __pycache__
│       ├── config.cpython-313.pyc
│       ├── db.cpython-313.pyc
│       ├── __init__.cpython-313.pyc
│       └── lifespan.cpython-313.pyc
├── database.db
├── di
│   ├── db.py
│   ├── gspread.py
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── gspread.cpython-313.pyc
│   │   ├── __init__.cpython-313.pyc
│   │   ├── repositories.cpython-313.pyc
│   │   └── services.cpython-313.pyc
│   ├── repositories.py
│   └── services.py
├── domain
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-313.pyc
│   │   └── student.cpython-313.pyc
│   └── student.py
├── handlers
│   ├── http
│   │   ├── handler.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── handler.cpython-313.pyc
│   │       └── __init__.cpython-313.pyc
│   ├── __init__.py
│   └── __pycache__
│       └── __init__.cpython-313.pyc
├── main.py
├── __pycache__
│   └── main.cpython-313.pyc
├── README.md
├── repositories
│   ├── __init__.py
│   ├── interfaces.py
│   ├── __pycache__
│   │   ├── __init__.cpython-313.pyc
│   │   ├── interfaces.cpython-313.pyc
│   │   └── student.cpython-313.pyc
│   └── student.py
├── requirements.txt
├── service_account.json
├── services
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-313.pyc
│   │   └── student.cpython-313.pyc
│   └── student.py
└── test_main.http

16 directories, 44 files

~/study/campus_manager master !1 ?1 ❯ tree -d .                                                                                      Py campus_manager 17:34:32
.
├── core
├── di
├── domain
├── handlers
│   └──  http
├── repositories
├── services
├── .env.example
├── README.md
├──  database.db
└── main.py

````

- `core/` — fundamental app setup, configuration  
- `di/` — dependency injection, wiring of components  
- `domain/` — domain models, business objects  
- `handlers/` — HTTP / API handlers / endpoints  
- `repositories/` — data access layer (e.g. wrapper for Google Sheets, local DB, etc.)  
- `services/` — business logic, application services  
- `main.py` — application entry point  

Note: The repository also includes a `database.db` (SQLite) file. That might be used for local persistence or caching.

---

## Setup & Installation
### Prerequisites

- Python 3.8+ (or whichever version you choose)  
- `pip` (Python package manager)  
- Google Cloud (for service account credentials)  
- Access to Google Sheets and Forms APIs  
- A Google account  

### Steps

1. **Clone the repository**  
    ```bash
       git clone https://github.com/tulasu/campus-manager.git
       cd campus-manager
    ````

2. **Create a virtual environment & activate it**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # on macOS / Linux  
   # or
   .\venv\Scripts\activate     # on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare `.env` file**
   Copy `.env.example` to `.env` and fill in necessary values (see the “Environment Variables / `.env`” section below).

5. **Place `service_account.json` in project root (or appropriate location)**
   This file will contain your Google service account credentials (see instructions later).

6. **(Optional) Initialize / migrate database**
   If the application uses a SQLite DB or similar local persistence (e.g. `database.db`), you may need to create tables or seed some data. Check the code for any migrations or initialization scripts.

---

## Running the Application

Once everything is installed and configured:

```bash
python main.py
```

This should start the server (e.g. Flask or other web framework). Then you can access the application via `http://localhost:5000` (or whatever port is configured).

If there are custom commands or settings (debug mode, host/port override), check `main.py` or configuration files.

---

## Google Sheets & Google Forms Integration

This project uses the Google Sheets API to read/write data into a spreadsheet (the “main table”) and reads responses coming from a Google Form.

Typical workflow:

1. A student fills out the Google Form → the response is stored in the linked spreadsheet (Google Forms auto-links to a sheet).
2. The application periodically or on-demand reads new responses from that sheet.
3. The app writes computed/derived data, assignments, status updates, etc., into other sheets or other columns.
4. The app’s UI or API lets administrators view / modify the sheet data.

The “main table” is essentially your Google Spreadsheet with rows representing student submissions and columns for different attributes (name, program, scores, assignment status, etc.).

You’ll need to know the sheet ID, sheet name, and column headers to map them in your code.

---

## Creating Your Own Spreadsheet & Service Account Credentials

If you want to replicate the setup in your own Google Cloud / Google Sheets environment, here’s how:

### 1. Create a Google Sheet (the main table)

* Go to Google Sheets → New spreadsheet
* Add column headers as needed (e.g. `Timestamp`, `Student Name`, `Program`, `Score`, `Assigned Room`, `Status`, etc.)
* Note down the **Spreadsheet ID** (the long string in the sheet URL)
* Optionally, share this sheet with your service account email (so that your app can read/write to it)

### 2. Create a Google Form and link it to the sheet (or use an existing one)

* In Google Forms, build your form fields (e.g. dropdowns, text, etc.)
* In *Responses* tab → click the green Sheets icon to link it to your spreadsheet
* Now form submissions will appear in the sheet automatically

### 3. Create a Google Cloud service account & `service_account.json`

* Go to Google Cloud Console → IAM & Admin → Service Accounts
* Create a new service account (e.g. `campus-manager-sa`)
* Assign necessary roles — typically `Editor` or more restrictive scope: “Sheets API Editor”
* Go to “Keys” for that service account → create a JSON key → download it
* Rename the downloaded file to `service_account.json` and place it into your project (or somewhere your code expects)
* In your spreadsheet, **share** (via Google Sheets UI) with that service account email (so the service account can access the sheet)

Your code will use that JSON to authenticate via the Google APIs client libraries.

---

## License

Include or mention the license under which your project is released (MIT, Apache, etc). If there isn’t one yet, you might add an `LICENSE` file.
