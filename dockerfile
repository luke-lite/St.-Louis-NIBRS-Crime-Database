# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# Copy the Pipfile and Pipfile.lock into the container at /app
COPY Pipfile Pipfile.lock /app/

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code into the container at /app
COPY . /app

# Initialize and upgrade the database
RUN pipenv run flask db init
RUN pipenv run flask db migrate
RUN pipenv run flask db upgrade
RUN pipenv run python backfill_db.py

# Define the command to run the application
# CMD ["pipenv", "run", "python", "app.py"]
CMD ["pipenv", "run", "gunicorn", "-w", "4" ,"-b", "0.0.0.0:8080", "wsgi:app"]