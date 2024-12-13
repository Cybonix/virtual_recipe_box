# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite for the database
RUN apt-get update && apt-get install -y sqlite3

# Expose the port your application listens on
EXPOSE 8000

# Define the default command to run on container start
CMD ["python", "virtual_recipe_box.py"]
