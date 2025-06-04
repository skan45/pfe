# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /factureapp



# Install system dependencies (for example, needed for psycopg2, opencv, etc.)
RUN apt-get update &&  apt-get install -y \
file \
libpq-dev \
build-essential \
libjpeg-dev \
zlib1g-dev \
tesseract-ocr \
netcat-openbsd \ 
libgl1-mesa-glx \
&& rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt /factureapp/requirements.txt

COPY entrypoint.sh /factureapp/entrypoint.sh 
RUN pip install --upgrade pip \
    && pip install -r requirements.txt\
    && chmod +x entrypoint.sh



# Copy the current directory contents into the container at /app
COPY . /factureapp/
    

# Expose the port the app runs on
EXPOSE 8000

# Set the environment variables (optional)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN ls -l /factureapp/entrypoint.sh && file /factureapp/entrypoint.sh
ENTRYPOINT ["/factureapp/entrypoint.sh"]

