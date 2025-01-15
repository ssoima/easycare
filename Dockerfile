FROM amazon/aws-lambda-python:3.13.2024.11.06.17

# Set the working directory inside the container
WORKDIR /workspace

# Create the directory explicitly
RUN mkdir -p /workspace/easycare

# Copy the folder from the host machine to the container
COPY . /workspace/easycare

# Create a virtual environment
RUN python -m venv /workspace/easycare/python

# Upgrade pip and install dependencies
RUN /workspace/easycare/python/bin/pip install --upgrade pip \
    && /workspace/easycare/python/bin/pip install -r /workspace/easycare/requirements.txt

# Command to keep the container running or start your application
CMD ["bash"]
