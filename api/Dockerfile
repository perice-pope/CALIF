# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Add a non-root user and switch to it
RUN useradd --create-home appuser
USER appuser

# Copy the requirements file into the container at /app
COPY --chown=appuser:appuser requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir and --user to install packages in the user's home directory
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application's code into the container
COPY --chown=appuser:appuser ./api /app/api

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application with uvicorn
# Use the non-root user's local bin directory
CMD ["/home/appuser/.local/bin/uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"] 