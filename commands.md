`python -m venv .venv` --> create virtual environment
`source .venv/bin/activate` --> activate virtual environment
`deactivate` --> deactivate virtual environment
`pip install -r requirements.txt` --> to install libraries from requirements.txt file
`pip freeze` or `pip freeze > file_name.txt` --> to see all installed libraries
`uvicorn app.app:app --reload` or `fastapi dev app/app.py`