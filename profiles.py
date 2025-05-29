# profiles.py
import json
import os
from datetime import datetime

USER_PROFILES_FILE = 'data/user_profiles.json'

def save_user_profile(user_id, profile_data):
    """Save user profile data"""
    profiles = load_user_profiles()
    profiles[user_id] = {
        'profile_data': profile_data,
        'created_at': datetime.now().isoformat()
    }
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(USER_PROFILES_FILE), exist_ok=True)
    
    with open(USER_PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=2)

def load_user_profiles():
    """Load all user profiles"""
    if not os.path.exists(USER_PROFILES_FILE):
        return {}
    try:
        with open(USER_PROFILES_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def get_user_profile(user_id):
    """Get a specific user's profile"""
    profiles = load_user_profiles()
    return profiles.get(user_id, {}).get('profile_data')

def save_training_data(training_data):
    """Save training data for model training"""
    TRAINING_DATA_FILE = 'data/training_data.json'
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(TRAINING_DATA_FILE), exist_ok=True)
    
    existing_data = []
    if os.path.exists(TRAINING_DATA_FILE):
        try:
            with open(TRAINING_DATA_FILE, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            pass
    
    existing_data.append({
        'data': training_data,
        'timestamp': datetime.now().isoformat()
    })
    
    with open(TRAINING_DATA_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2)