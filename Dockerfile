# Use the official Playwright image which includes Python and Browsers
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements (if any) and install dependencies
# We pin the version to match the base image to avoid browser binary mismatch
# Also installing google-generativeai for AI essay writing
RUN pip install playwright==1.40.0 google-generativeai

# Copy the application code
COPY . .

# Command to run the application
# We use a dummy command here so the container stays alive for us to exec into it
CMD ["tail", "-f", "/dev/null"]
