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

# Copy the rest of the application's code
COPY --chown=appuser:appuser . .

# Make sure the script is executable
RUN chmod +x /app/slack_bot/notify.py

# Set environment variables for the function
# The PORT is set by Cloud Functions at runtime.
ENV FUNCTION_TARGET=notify_slack
ENV FUNCTION_SOURCE=slack_bot/notify.py

# Run the functions framework to host the function
# Use the non-root user's local bin directory
# This CMD is for local testing with `docker run`.
CMD ["/home/appuser/.local/bin/functions-framework", "--target=notify_slack", "--source=slack_bot/notify.py"] 