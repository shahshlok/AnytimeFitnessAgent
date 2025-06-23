# Step 1: Use an official Python runtime as a parent image
# We're using python:3.12-slim which is a lightweight and official image.
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
# This is where our application code will live.
WORKDIR /app

# Step 3: Copy the requirements file from the root directory
# The build context is ai_agent/backend/, so we go up two levels to the root.
# This step is done separately to leverage Docker's layer caching.
# If requirements.txt doesn't change, Docker won't re-install dependencies on every build.
COPY ../../requirements.txt .

# Step 4: Install any needed packages specified in requirements.txt
# --no-cache-dir makes the image smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your application's code into the container
# This copies everything from ai_agent/backend/ into /app in the container.
COPY . .

# Step 6: Expose the port your app runs on
# This is documentation for Docker. It doesn't actually publish the port to the host.
# Your uvicorn command runs on 7479, so we expose that.
EXPOSE 7479

# Step 7: Define the command to run your app
# This command is executed when the container starts.
# --host 0.0.0.0 is crucial to make the server accessible from outside the container.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7479"]