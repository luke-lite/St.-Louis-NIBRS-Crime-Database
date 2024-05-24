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

# Run the application
# CMD ["pipenv", "run", "python", "server.py"]
CMD ["pipenv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "app:app"]