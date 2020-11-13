# Use the official Python image as the base image
FROM python:3.9

# Set environment variables for Python buffering and UTF-8 encoding
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

# Set the working directory in the container
WORKDIR /code

# Copy the requirements.txt file to the container
COPY requirements.txt /code/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files to the container
COPY . /code/

# Expose the port that the Django application will run on (change it if necessary)
EXPOSE 8000

# Run the Django development server when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
