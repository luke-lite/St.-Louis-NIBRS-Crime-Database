# Use the official lightweight Python image for Python 3.10.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install pipenv and project dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . .

# Initialize and upgrade the database
RUN pipenv run flask db init || true  # Allow failure if already initialized
RUN pipenv run flask db migrate || true  # Allow failure if no changes
RUN pipenv run flask db upgrade
RUN pipenv run python backfill_db.py

# Run the application
CMD ["pipenv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "app:app"]

# Run the application locally:
# CMD ["pipenv", "run", "python", "server.py"]