"""
Facebook Ads Automation Application

This application provides both a web interface and script functionality to automate Facebook ad campaigns:
- Creating a campaign with a specified budget
- Setting up an ad set with targeting parameters
- Creating an ad creative with text and image
- Generating an ad

All components are created in PAUSED state to prevent accidental spending.
"""

# Import the Flask app for the web interface
from app import app

# Imports for the script functionality
import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

def authenticate_facebook_api():
    """
    Authenticate with the Facebook Ads API using the access token from environment variables.
    Returns the authenticated AdAccount object.
    """
    try:
        # Get credentials from environment variables
        access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
        ad_account_id = os.environ.get('AD_ACCOUNT_ID')
        
        if not access_token or not ad_account_id:
            raise ValueError("Missing required environment variables. Please set FACEBOOK_ACCESS_TOKEN and AD_ACCOUNT_ID in Replit Secrets.")
        
        # Initialize the Facebook Ads API
        FacebookAdsApi.init(access_token=access_token)
        
        # Get the Ad Account
        ad_account = AdAccount(ad_account_id)
        
        # Verify connection by fetching account name
        account_details = ad_account.api_get(fields=['name'])
        print(f"Successfully connected to Facebook Ads account: {account_details['name']}")
        
        return ad_account
    
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise

def create_campaign(ad_account, name="Fitness Campaign", objective="REACH", daily_budget=5000):
    """
    Create a new campaign with specified parameters.
    
    Args:
        ad_account: The authenticated AdAccount object
        name: Campaign name
        objective: Campaign objective (default: REACH)
        daily_budget: Daily budget in cents (default: 5000 = $50)
        
    Returns:
        campaign_id: ID of the created campaign
    """
    try:
        # Create a new campaign
        campaign = Campaign(parent_id=ad_account['id'])
        campaign.update({
            'name': name,
            'objective': objective,
            'status': 'PAUSED',  # Always start paused for safety
            'special_ad_categories': [],
        })
        
        # Create the campaign in Facebook
        campaign.api_create()
        campaign_id = campaign.get_id()
        
        print(f"Campaign created successfully. Campaign ID: {campaign_id}")
        return campaign_id
    
    except Exception as e:
        print(f"Campaign creation error: {str(e)}")
        raise

def create_ad_set(ad_account, campaign_id, name="Fitness Ad Set", daily_budget=5000):
    """
    Create an ad set with targeting for 25-35-year-old US women interested in fitness.
    
    Args:
        ad_account: The authenticated AdAccount object
        campaign_id: ID of the parent campaign
        name: Ad set name
        daily_budget: Daily budget in cents (default: 5000 = $50)
        
    Returns:
        ad_set_id: ID of the created ad set
    """
    try:
        # Create an ad set
        ad_set = AdSet(parent_id=ad_account['id'])
        ad_set.update({
            'name': name,
            'campaign_id': campaign_id,
            'daily_budget': daily_budget,
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': 'REACH',
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'targeting': {
                'geo_locations': {
                    'countries': ['US']
                },
                'age_min': 25,
                'age_max': 35,
                'genders': [2],  # 2 = female
                'interests': [
                    {'id': '6003107902433', 'name': 'Fitness'}
                ],
            },
            'status': 'PAUSED',
        })
        
        # Create the ad set in Facebook
        ad_set.api_create()
        ad_set_id = ad_set.get_id()
        
        print(f"Ad set created successfully. Ad Set ID: {ad_set_id}")
        return ad_set_id
    
    except Exception as e:
        print(f"Ad set creation error: {str(e)}")
        raise

def create_ad_creative(ad_account, page_id, message="Get Fit Now!"):
    """
    Create an ad creative with specified text.
    
    Args:
        ad_account: The authenticated AdAccount object
        page_id: ID of the Facebook Page to associate with the ad
        message: Ad message text
        
    Returns:
        creative_id: ID of the created ad creative
    """
    try:
        # Get page_id from environment variables if not provided
        if not page_id:
            page_id = os.environ.get('FACEBOOK_PAGE_ID')
            if not page_id:
                raise ValueError("Facebook Page ID is required. Please set FACEBOOK_PAGE_ID in Replit Secrets.")
        
        # Create the ad creative
        creative = AdCreative(parent_id=ad_account['id'])
        creative.update({
            'name': 'Fitness Ad Creative',
            'object_story_spec': {
                'page_id': page_id,
                'link_data': {
                    'link': 'https://example.com',
                    'message': message,
                    # Note: For a real implementation, you would need to upload an image
                    # and get its hash. For simplicity, we're skipping that step here.
                }
            }
        })
        
        # Create the ad creative in Facebook
        creative.api_create()
        creative_id = creative.get_id()
        
        print(f"Ad creative created successfully. Creative ID: {creative_id}")
        return creative_id
    
    except Exception as e:
        print(f"Ad creative creation error: {str(e)}")
        raise

def create_ad(ad_account, ad_set_id, creative_id, name="Fitness Ad"):
    """
    Create an ad using the specified ad set and creative.
    
    Args:
        ad_account: The authenticated AdAccount object
        ad_set_id: ID of the parent ad set
        creative_id: ID of the ad creative to use
        name: Ad name
        
    Returns:
        ad_id: ID of the created ad
    """
    try:
        # Create the ad
        ad = Ad(parent_id=ad_account['id'])
        ad.update({
            'name': name,
            'adset_id': ad_set_id,
            'creative': {'creative_id': creative_id},
            'status': 'PAUSED',
        })
        
        # Create the ad in Facebook
        ad.api_create()
        ad_id = ad.get_id()
        
        print(f"Ad created successfully. Ad ID: {ad_id}")
        return ad_id
    
    except Exception as e:
        print(f"Ad creation error: {str(e)}")
        raise

def main():
    """
    Main function to run the Facebook ads automation script.
    """
    try:
        print("Starting Facebook Ads Automation...")
        
        # Step 1: Authenticate with the Facebook Ads API
        ad_account = authenticate_facebook_api()
        
        # Step 2: Create a campaign
        campaign_id = create_campaign(ad_account)
        
        # Step 3: Create an ad set with targeting
        ad_set_id = create_ad_set(ad_account, campaign_id)
        
        # Step 4: Create an ad creative
        # Note: You need to provide a Facebook Page ID
        page_id = os.environ.get('FACEBOOK_PAGE_ID')
        creative_id = create_ad_creative(ad_account, page_id)
        
        # Step 5: Create an ad
        ad_id = create_ad(ad_account, ad_set_id, creative_id)
        
        # Summary
        print("\nFacebook Ads Automation Complete!")
        print("--------------------------------")
        print(f"Campaign ID: {campaign_id}")
        print(f"Ad Set ID: {ad_set_id}")
        print(f"Creative ID: {creative_id}")
        print(f"Ad ID: {ad_id}")
        print(f"\nAll components are created in PAUSED state. Log in to Ads Manager to review before activating.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Facebook Ads Automation failed.")

if __name__ == "__main__":
    main()
