from flask import Flask, render_template, request, redirect, url_for
import joblib
from ml_model.outfit_engine import recommend_outfits, save_outfit_selection
from google.oauth2 import service_account
from apscheduler.schedulers.background import BackgroundScheduler
from google import genai
from flask import Flask, render_template, request, redirect, url_for
import joblib
from datetime import datetime
from profiles import save_user_profile, get_user_profile, save_training_data
from training import create_initial_model
from outfit_generator import generate_outfit_recommendations
import json
from training import create_initial_model
import os


# Create a directory to store user data
USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'user_data')
os.makedirs(USER_DATA_DIR, exist_ok=True)


app = Flask(__name__, template_folder='templates', static_folder='static')

# Load model and encoders with joblib
encoder = joblib.load("model/encoders.joblib")
label_encoder = joblib.load("model/label_encoder.joblib")
model = joblib.load("model/model.joblib")

# Initialize Gemini client with service account credentials
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'data', 'Api.json')

# Load credentials
with open(SERVICE_ACCOUNT_FILE, 'r') as f:
    service_account_info = json.load(f)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )

# Initialize Gemini client with project details
PROJECT_ID = service_account_info['project_id']
genai_client = genai.Client(
    vertexai=True,
    credentials=credentials,
    project=PROJECT_ID,
    location="us-central1"
)

def generate_outfit_description(user_input, recommended_outfits):
    prompt = f"""
    A user has provided the following style-related input:
    - Skin tone: {user_input['skin_tone']}
    - Style preference: {user_input['style']}
    - Body shape: {user_input['body_shape']}
    - Height: {user_input['height']} cm
    - Clothing size: {user_input['size']}
    - Gender: {user_input['gender']}

    The system has recommended these outfit options:
    {', '.join(recommended_outfits)}

    Please describe three suitable outfit for this user, including colors and reasons why it matches the preferences.
    """

    response = genai_client.generate_content(
        model="gemini-pro",
        contents=prompt
    )
    return response.text.strip()


# @app.route('/outfit', methods=['POST'])
# def index():
#     if request.method == 'POST':
#         user_input = {
#             'skin_tone': request.form['skin_tone'],
#             'style': request.form['style'],
#             'body_shape': request.form['body_shape'],
#             'height': float(request.form['height']),
#             'size': request.form['size'],
#             'gender': request.form['gender']
#         }

#         # Get the list of recommended outfits
#         outfits = recommend_outfits(user_input, model, encoder)
        
#         # Generate the description
#         outfit_description = generate_outfit_description(user_input, outfits)
        
    #     # Create a list of dictionaries with image and description
    #     outfit_data = []
    #     for outfit in outfits:
    #         outfit_data.append({
    #             'image': f'images/{outfit.lower().replace(" ", "_")}.jpg',  # Adjust this path as needed
    #             'description': outfit_description
    #         })

    #     return render_template('results.html', outfits=outfit_data)

    # return render_template('index.html')
# @app.route('/outfit', methods=['POST'])
# def outfit():
#     if request.method == 'POST':
#         user_input = {
#             'name': request.form['name'],
#             'gender': request.form['gender'],
#             'age': request.form['age'],
#             'height': request.form['height'],
#             'size': request.form['size'],
#             'skin_tone': request.form['skin']
#         }

#         # Convert height range to average value
#         height_range = user_input['height'].split('-')
#         user_input['height'] = (int(height_range[0]) + int(height_range[1])) / 2

#         # Get recommendations (for now, just return some sample data)
#         outfits = [
#             {'description': f'Casual outfit for {user_input["gender"]} with {user_input["skin_tone"]} skin tone'},
#             {'description': f'Business outfit for {user_input["gender"]} with {user_input["skin_tone"]} skin tone'},
#             {'description': f'Evening outfit for {user_input["gender"]} with {user_input["skin_tone"]} skin tone'}
#         ]

#         return render_template('results.html', outfits=outfits, user=user_input)

#     return render_template('index.html')
@app.route('/outfit', methods=['POST'])
def outfit():
    if request.method == 'POST':
        user_data = {
            'name': request.form['name'],
            'gender': request.form['gender'],
            'age': request.form['age'],
            'height': request.form['height'],
            'size': request.form['size'],
            'skin_tone': request.form['skin']
        }
        
        # Generate user ID (you can use any unique identifier)
        user_id = request.form['name'].lower().replace(' ', '_')
        
        # Save user profile
        save_user_profile(user_id, user_data)
        
        # Redirect to daily outfit recommendation page
        return redirect(url_for('daily_recommendation', user_id=user_id))


@app.route('/daily/<user_id>', methods=['GET', 'POST'])
def daily_recommendation(user_id):
    if request.method == 'POST':
        try:
            # Get user profile and preferences
            user_profile = get_user_profile(user_id)
            if not user_profile:
                return "User profile not found", 404
                
            # Get daily data from form
            daily_data = {
                'weather': request.form.get('weather'),
                'occasion': request.form.get('occasion'),
                'mood': request.form.get('mood')
            }
            
            # Combine profile and daily data
            combined_data = {
                **user_profile,
                **daily_data,
                'user_id': user_id
            }
            
            # Get previously chosen outfits to avoid repetition
            history_path = 'data/history.json'
            if os.path.exists(history_path):
                try:
                    with open(history_path, 'r') as f:
                        user_history = json.load(f)
                        combined_data['previous_outfits'] = user_history.get(user_id, [])
                except (json.JSONDecodeError, FileNotFoundError):
                    combined_data['previous_outfits'] = []
            else:
                combined_data['previous_outfits'] = []
            
            # Generate new outfits (excluding previous ones)
            outfits = generate_outfit_recommendations(combined_data)
            
            # Get previous outfits for the template
            previous_outfits = combined_data.get('previous_outfits', [])
            
            # If no outfits were generated, show a message
            if not outfits:
                return render_template('outfit.html',
                                    outfits=[],
                                    user=user_profile,
                                    daily_data=daily_data,
                                    user_id=user_id,
                                    previous_outfits=previous_outfits,
                                    message="No new outfit recommendations available. Please try different preferences.")
            
            # Save training data entry
            training_entry = {
                'user_id': user_id,
                **user_profile,
                'preferences': daily_data,
                'outfits': [outfit.get('type', 'unknown') for outfit in outfits],
                'chosen_outfit': None,
                'date': datetime.now().isoformat(),
                'timestamp': datetime.now().timestamp()
            }
            
            save_training_data(training_entry)
            
            return render_template('outfit.html', 
                                outfits=outfits, 
                                user=user_profile,
                                daily_data=daily_data,
                                user_id=user_id,
                                previous_outfits=previous_outfits)
                                
        except Exception as e:
            print(f"Error in daily_recommendation: {str(e)}")
            return f"An error occurred: {str(e)}", 500
    
    return render_template('daily_form.html', user_id=user_id)

@app.route('/choose_outfit', methods=['POST'])
def choose_outfit():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
        user_id = data.get('user_id')
        outfit_type = data.get('outfit_type')
        
        if not user_id or not outfit_type:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Load existing training data
        file_path = 'data/training_data.json'
        training_data = []
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    training_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                training_data = []
        
        # Get user profile
        user_profile = get_user_profile(user_id) or {}
        
        # Create a new training entry
        training_entry = {
            'user_id': user_id,
            'preferences': user_profile.get('preferences', {}),
            'outfits': [],
            'chosen_outfit': outfit_type,
            'date': datetime.now().isoformat(),
            'timestamp': datetime.now().timestamp()
        }
        
        # Add the new entry
        training_data.append(training_entry)
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(training_data, f, indent=2)
        
        # Update user's outfit history
        history_path = 'data/history.json'
        user_history = {}
        
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    user_history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                user_history = {}
        
        if user_id not in user_history:
            user_history[user_id] = []
            
        # Add to history if not already present
        if outfit_type not in user_history[user_id]:
            user_history[user_id].append(outfit_type)
            
        with open(history_path, 'w') as f:
            json.dump(user_history, f, indent=2)
        
        return json.dumps({
            'status': 'success',
            'message': 'Outfit selection saved successfully',
            'outfit_type': outfit_type
        }), 200, {'ContentType': 'application/json'}
        
    except Exception as e:
        print(f"Error in choose_outfit: {str(e)}")
        return json.dumps({
            'status': 'error',
            'message': 'Failed to save outfit selection'
        }), 500, {'ContentType': 'application/json'}
    
    return render_template('daily_form.html', user_id=user_id)


# @app.route('/daily/<user_id>', methods=['GET', 'POST'])
# def daily_recommendation(user_id):
#     if request.method == 'POST':
#         # Get daily preferences
#         daily_data = {
#             'weather': request.form['weather'],
#             'occasion': request.form['occasion'],
#             'mood': request.form['mood'],
#             'date': datetime.now().strftime('%Y-%m-%d')
#         }
        
#         # Get user profile
#         user_profile = get_user_profile(user_id)
        
#         # Combine profile and daily data
#         combined_data = {**user_profile, **daily_data}
        
#         # Generate outfit recommendations using Gemini
#         outfits = generate_outfit_recommendations(combined_data)
        
#         return render_template('outfit.html', outfits=outfits, user=user_profile)
    
#     return render_template('daily_form.html')


@app.route('/')
def home():
    return render_template('index.html')


# @app.route('/')
# def home():
#     if not session.get('is_logged_in'):
#         return redirect(url_for('login'))
#     return f"Welcome{session.get('name')}"


@app.route('/save', methods=['POST'])
def save():
    chosen_index = int(request.form['chosen'])
    user_id = request.form['user_id']
    
    # Load user profile
    user_profile = get_user_profile(user_id)
    
    # Load daily data (you might want to store this in a session or database)
    daily_data = {
        'weather': request.form['weather'],
        'occasion': request.form['occasion'],
        'mood': request.form['mood'],
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Combine all data
    training_data = {
        'user_profile': user_profile,
        'daily_data': daily_data,
        'chosen_outfit': chosen_index
    }
    
    # Save training data
    save_training_data(training_data)
    
    # Train model
    train_model_with_user_data()
    
    return redirect(url_for('daily_recommendation', user_id=user_id))



@app.route('/api/recommend', methods=['POST'])
def recommend_outfit_api():
    try:
        data = request.get_json()
        required_fields = ['skin_tone', 'style', 'body_shape', 'height', 'size', 'gender']
        
        if not all(field in data for field in required_fields):
            return {'error': 'Missing required fields'}, 400
            
        recommendations = recommend_outfits(data, model, encoder)
        description = generate_outfit_description(data, recommendations)
        
        return {
            'status': 'success',
            'recommendations': recommendations,
            'description': description
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500

from training import train_model_with_user_data

@app.route('/train', methods=['POST'])
def train():
    try:
        train_model_with_user_data()
        return {'status': 'success', 'message': 'Model trained successfully'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500



def schedule_training():
    scheduler = BackgroundScheduler()
    scheduler.add_job(train_model_with_user_data, 'interval', hours=1)
    scheduler.start()

if __name__ == '__main__':
    # Create initial model if it doesn't exist
    try:
        joblib.load("model/model.joblib")
    except:
        create_initial_model()
    
    # Initialize scheduler and run app
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(train_model_with_user_data, 'interval', hours=1)
    scheduler.start()
    
    app.run(debug=True)

