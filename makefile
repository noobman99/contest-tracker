run_development:
	@echo "Running development environment..."
	@python app.py

run_deployment:
	@echo "Running deployment environment..."
	@waitress-serve --port=8080 app:app

