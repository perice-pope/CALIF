# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Add a non-root user and switch to it
RUN useradd --create-home appuser
USER appuser

# Copy the requirements file into the container
COPY --chown=appuser:appuser requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the application code
COPY --chown=appuser:appuser ./dashboard /app/dashboard

# Expose the port that Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app
# Use the non-root user's local bin directory
CMD ["/home/appuser/.local/bin/streamlit", "run", "dashboard/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 