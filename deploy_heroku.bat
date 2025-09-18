# Heroku Deployment Script
@"
#!/bin/bash
# Deploy FHIR App to Heroku

echo " Deploying FHIR App to Heroku..."

# Install Heroku CLI if not installed
if ! command -v heroku &> /dev/null; then
    echo "Installing Heroku CLI..."
    # Download and install Heroku CLI
    echo "Please install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli"
fi

# Login to Heroku
heroku login

# Create Heroku app
heroku create fhir-converter-app

# Set environment variables
heroku config:set FLASK_ENV=production

# Deploy
git add .
git commit -m "Deploy FHIR converter app"
git push heroku main

# Open the app
heroku open

echo " App deployed! Share this URL with your team:"
heroku apps:info --json | findstr web_url
