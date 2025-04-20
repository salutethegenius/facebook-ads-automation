from flask import Flask, render_template, request, flash, session, redirect, url_for
import os
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-dev-secret-key")

@app.route('/')
def index():
    """Main page for Facebook Ads Automation tool"""
    return render_template('index.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Authenticate with Facebook Ads API"""
    try:
        # Get credentials from form or environment variables
        access_token = request.form.get('access_token') or os.environ.get('FACEBOOK_ACCESS_TOKEN')
        ad_account_id = request.form.get('ad_account_id') or os.environ.get('AD_ACCOUNT_ID')
        
        if not access_token or not ad_account_id:
            flash("Missing credentials. Please provide access token and ad account ID.", "error")
            return redirect(url_for('index'))
        
        # Store in session for later use
        session['access_token'] = access_token
        session['ad_account_id'] = ad_account_id
        
        # Initialize the Facebook Ads API
        FacebookAdsApi.init(access_token=access_token)
        
        # Get the Ad Account
        ad_account = AdAccount(ad_account_id)
        
        # Verify connection by fetching account name
        account_details = ad_account.api_get(fields=['name', 'account_status'])
        
        flash(f"Successfully connected to Facebook Ads account: {account_details['name']}", "success")
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard to create campaigns after authentication"""
    if 'access_token' not in session or 'ad_account_id' not in session:
        flash("You need to authenticate first", "error")
        return redirect(url_for('index'))
    
    return render_template('dashboard.html')

@app.route('/create_campaign', methods=['POST'])
def create_campaign_route():
    """Create a Facebook Ads campaign with specified parameters"""
    if 'access_token' not in session or 'ad_account_id' not in session:
        flash("You need to authenticate first", "error")
        return redirect(url_for('index'))
    
    try:
        # Get form data
        name = request.form.get('campaign_name', 'Fitness Campaign')
        objective = request.form.get('objective', 'REACH')
        daily_budget = int(float(request.form.get('daily_budget', '50')) * 100)  # Convert to cents
        
        # Initialize API
        FacebookAdsApi.init(access_token=session['access_token'])
        ad_account = AdAccount(session['ad_account_id'])
        
        # Create campaign
        campaign = Campaign(parent_id=ad_account['id'])
        campaign.update({
            'name': name,
            'objective': objective,
            'status': 'PAUSED',  # Always start paused for safety
            'special_ad_categories': [],
        })
        
        campaign.api_create()
        campaign_id = campaign.get_id()
        
        # Store in session
        session['campaign_id'] = campaign_id
        
        flash(f"Campaign created successfully. Campaign ID: {campaign_id}", "success")
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f"Campaign creation error: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/create_ad_set', methods=['POST'])
def create_ad_set_route():
    """Create an ad set for the campaign"""
    if 'access_token' not in session or 'ad_account_id' not in session or 'campaign_id' not in session:
        flash("You need to create a campaign first", "error")
        return redirect(url_for('dashboard'))
    
    try:
        # Get form data
        name = request.form.get('ad_set_name', 'Fitness Ad Set')
        daily_budget = int(float(request.form.get('daily_budget', '50')) * 100)  # Convert to cents
        age_min = int(request.form.get('age_min', '25'))
        age_max = int(request.form.get('age_max', '35'))
        countries = request.form.get('countries', 'US').split(',')
        gender = int(request.form.get('gender', '2'))  # 2 = female
        
        # Initialize API
        FacebookAdsApi.init(access_token=session['access_token'])
        ad_account = AdAccount(session['ad_account_id'])
        
        # Create ad set
        ad_set = AdSet(parent_id=ad_account['id'])
        ad_set.update({
            'name': name,
            'campaign_id': session['campaign_id'],
            'daily_budget': daily_budget,
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': 'REACH',
            'bid_strategy': 'LOWEST_COST_WITHOUT_CAP',
            'targeting': {
                'geo_locations': {
                    'countries': countries
                },
                'age_min': age_min,
                'age_max': age_max,
                'genders': [gender],
                'interests': [
                    {'id': '6003107902433', 'name': 'Fitness'}
                ],
            },
            'status': 'PAUSED',
        })
        
        ad_set.api_create()
        ad_set_id = ad_set.get_id()
        
        # Store in session
        session['ad_set_id'] = ad_set_id
        
        flash(f"Ad set created successfully. Ad Set ID: {ad_set_id}", "success")
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f"Ad set creation error: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/create_ad_creative', methods=['POST'])
def create_ad_creative_route():
    """Create an ad creative for the campaign"""
    if 'access_token' not in session or 'ad_account_id' not in session:
        flash("You need to authenticate first", "error")
        return redirect(url_for('dashboard'))
    
    try:
        # Get form data
        page_id = request.form.get('page_id') or os.environ.get('FACEBOOK_PAGE_ID')
        message = request.form.get('message', 'Get Fit Now!')
        link = request.form.get('link', 'https://example.com')
        
        if not page_id:
            flash("Facebook Page ID is required", "error")
            return redirect(url_for('dashboard'))
        
        # Initialize API
        FacebookAdsApi.init(access_token=session['access_token'])
        ad_account = AdAccount(session['ad_account_id'])
        
        # Create ad creative
        creative = AdCreative(parent_id=ad_account['id'])
        creative.update({
            'name': 'Fitness Ad Creative',
            'object_story_spec': {
                'page_id': page_id,
                'link_data': {
                    'link': link,
                    'message': message,
                    # Note: For a real implementation, you would need to upload an image
                    # and get its hash. For simplicity, we're skipping that step here.
                }
            }
        })
        
        creative.api_create()
        creative_id = creative.get_id()
        
        # Store in session
        session['creative_id'] = creative_id
        
        flash(f"Ad creative created successfully. Creative ID: {creative_id}", "success")
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f"Ad creative creation error: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/create_ad', methods=['POST'])
def create_ad_route():
    """Create an ad using the ad set and creative"""
    if ('access_token' not in session or 'ad_account_id' not in session or 
            'ad_set_id' not in session or 'creative_id' not in session):
        flash("You need to create an ad set and ad creative first", "error")
        return redirect(url_for('dashboard'))
    
    try:
        # Get form data
        name = request.form.get('ad_name', 'Fitness Ad')
        
        # Initialize API
        FacebookAdsApi.init(access_token=session['access_token'])
        ad_account = AdAccount(session['ad_account_id'])
        
        # Create ad
        ad = Ad(parent_id=ad_account['id'])
        ad.update({
            'name': name,
            'adset_id': session['ad_set_id'],
            'creative': {'creative_id': session['creative_id']},
            'status': 'PAUSED',
        })
        
        ad.api_create()
        ad_id = ad.get_id()
        
        # Store in session
        session['ad_id'] = ad_id
        
        flash(f"Ad created successfully. Ad ID: {ad_id}", "success")
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f"Ad creation error: {str(e)}", "error")
        return redirect(url_for('dashboard'))

@app.route('/summary')
def summary():
    """Display a summary of created components"""
    if 'access_token' not in session or 'ad_account_id' not in session:
        flash("You need to authenticate first", "error")
        return redirect(url_for('index'))
    
    # Collect all IDs we have in session
    campaign_id = session.get('campaign_id', 'Not created')
    ad_set_id = session.get('ad_set_id', 'Not created')
    creative_id = session.get('creative_id', 'Not created')
    ad_id = session.get('ad_id', 'Not created')
    
    return render_template('summary.html', 
                          campaign_id=campaign_id,
                          ad_set_id=ad_set_id,
                          creative_id=creative_id,
                          ad_id=ad_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)