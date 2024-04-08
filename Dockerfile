FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt read_car.py .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the application
CMD [ "python", "read_car.py" ]