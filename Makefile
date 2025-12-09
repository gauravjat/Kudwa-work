.PHONY: install setup load-data run clean help

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Initialize database"
	@echo "  make load-data   - Load financial data into database"
	@echo "  make run         - Start the API server"
	@echo "  make clean       - Remove database and cache files"

install:
	pip install -r requirements.txt

setup:
	@echo "Setting up database..."
	python -c "from app.database import init_db; init_db()"
	@echo "✅ Database initialized"

load-data:
	@echo "Loading financial data..."
	python load_data.py

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	rm -f financial_data.db
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete


