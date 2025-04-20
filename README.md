# Facebook Ads Automation

A web application and script to automate the creation of Facebook ad campaigns using the Facebook Ads API.

## Overview

This project provides two ways to automate Facebook ad campaigns:

1. **Web Interface**: A user-friendly Flask web application to create campaigns, ad sets, ad creatives, and ads through forms
2. **Script**: A Python script for automated, programmatic campaign creation

Both methods create a full Facebook ad campaign setup:
- Campaign with a configurable daily budget and objective (default: $50 daily, "REACH" objective)
- Ad set targeting 25-35-year-old US women interested in fitness (customizable)
- Ad creative with the message "Get Fit Now!"
- Everything is created in PAUSED state for safety

## Features

- Full campaign creation workflow
- Targeting configuration through web forms
- Input validation and error handling
- Secure credential management
- Campaign summary with all generated IDs

## Prerequisites

- Facebook Developer Account with:
  - An app registered at [Facebook for Developers](https://developers.facebook.com)
  - Access token with `ads_management` permissions
  - Ad Account ID
  - Facebook Page ID (for the ad creative)

## Setup

### Environment Variables

The application requires the following environment variables:

- `FACEBOOK_ACCESS_TOKEN`: Your Facebook access token with ads_management permissions
- `AD_ACCOUNT_ID`: Your ad account ID (format: `act_123456789`)
- `FACEBOOK_PAGE_ID`: ID of your Facebook Page
- `SESSION_SECRET`: Secret key for securing Flask sessions

In Replit, these can be set in the Secrets tab.

### Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install facebook-business flask gunicorn
   ```

## Usage

### Web Interface

1. Start the Flask application:
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```
2. Navigate to the application in your web browser
3. Authenticate with your Facebook credentials
4. Follow the step-by-step forms to create your campaign

### Python Script

Run the script directly:
```
python main.py
```

This will execute the automated campaign creation process using the environment variables for authentication.

## Safety Features

- All ads are created in PAUSED state to prevent accidental spending
- Review step before campaign activation
- Validation of inputs and API responses

## License

MIT License
