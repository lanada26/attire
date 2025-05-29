# # training.py
# import json
# import os
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder
# import numpy as np
# import pickle

# def load_training_data():
#     """Load training data from a JSON file"""
#     try:
        
#         # Extract label (chosen outfit type)
#         labels.append(entry['outfits'][entry['chosen']]['type'])
    
#     # Convert categorical data to numerical
#     encoders = {}
#     for i in range(len(features[0])):
#         encoder = LabelEncoder()
#         features[:, i] = encoder.fit_transform(features[:, i])
#         encoders[i] = encoder
    
#     # Convert to numpy arrays
#     features = np.array(features)
#     labels = np.array(labels)
    
#     # Train the model
#     model = RandomForestClassifier(n_estimators=100)
#     model.fit(features, labels)
    
#     # Save the model and encoders
#     with open('model/model.pkl', 'wb') as f:
#         pickle.dump(model, f)
    
#     with open('model/encoders.pkl', 'wb') as f:
#         pickle.dump(encoders, f)
    
#     print("Model trained and saved to 'model/' directory")# import os
import glob
import json
from datetime import datetime
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
import os
import glob
import json
from datetime import datetime
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

def generate_user_id():
    """Generate a unique user ID"""
    return datetime.now().strftime('%Y%m%d_%H%M%S_%f')

def load_user_data():
    """Load all user data from saved files"""
    USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'user_data')
    user_files = glob.glob(os.path.join(USER_DATA_DIR, 'user_*.json'))
    training_data = []
    
    for file in user_files:
        with open(file, 'r') as f:
            user_data = json.load(f)
            training_data.append({
                'input': user_data['preferences'],
                'output': user_data['chosen_outfit']
            })
    
    return training_data

def prepare_training_data(training_data, encoder):
    """Prepare data for training"""
    X = []
    y = []
    
    for data in training_data:
        input_data = {
            'skin_tone': encoder['skin_tone'].transform([data['input']['skin_tone']])[0],
            'style': encoder['style'].transform([data['input']['style']])[0],
            'body_shape': encoder['body_shape'].transform([data['input']['body_shape']])[0],
            'height': data['input']['height'],
            'size': encoder['size'].transform([data['input']['size']])[0],
            'gender': encoder['gender'].transform([data['input']['gender']])[0]
        }
        
        X.append(list(input_data.values()))
        y.append(data['output'])
    
    return np.array(X), y
def train_model_with_user_data():
    training_data = load_training_data()
    
    if not training_data:
        print("No training data available")
        return None
    
    X = []
    y = []
    
    for data in training_data:
        # Get the occasion from the data
        occasion = data.get('preferences', {}).get('occasion', 'casual')
        
        # Create feature vector
        features = [
            data.get('gender', 'other'),
            data.get('age', '20-30'),
            data.get('height', '160-170'),
            data.get('size', 'M'),
            data.get('skin_tone', 'medium'),
            occasion,
            data.get('preferences', {}).get('weather', 'clear'),
            data.get('preferences', {}).get('mood', 'relaxed')
        ]
        
        # Initialize encoders if they don't exist
        if 'encoders' not in train_model_with_user_data.__dict__:
            train_model_with_user_data.encoders = [LabelEncoder() for _ in range(len(features))]
            for i, encoder in enumerate(train_model_with_user_data.encoders):
                # Get all possible values for this feature
                all_values = [d.get('gender', 'other') if i == 0 else 
                             d.get('age', '20-30') if i == 1 else
                             d.get('height', '160-170') if i == 2 else
                             d.get('size', 'M') if i == 3 else
                             d.get('skin_tone', 'medium') if i == 4 else
                             d.get('preferences', {}).get('occasion', 'casual') if i == 5 else
                             d.get('preferences', {}).get('weather', 'clear') if i == 6 else
                             d.get('preferences', {}).get('mood', 'relaxed')
                             for d in training_data]
                encoder.fit(list(set(all_values)))
        
        # Encode features
        encoded_features = []
        for i, feature in enumerate(features):
            if feature in train_model_with_user_data.encoders[i].classes_:
                encoded_features.append(train_model_with_user_data.encoders[i].transform([feature])[0])
            else:
                # Handle unknown categories
                encoded_features.append(0)  # Default to first category
        
        X.append(encoded_features)
        y.append(data.get('chosen_outfit', 'casual'))
    
    # Train the model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    
    # Save the model and encoders
    os.makedirs('model', exist_ok=True)
    joblib.dump(model, 'model/model.joblib')
    joblib.dump(train_model_with_user_data.encoders, 'model/encoders.joblib')
    
    print("Model retrained with new data")
    return model



# test model 

# In training.py, add this at the end:
def create_initial_model():
    """Create and save initial model and encoders"""
    # Create dummy data for initial model
    X = np.array([
        [1, 2, 3, 170, 4, 5],
        [2, 3, 4, 165, 5, 6],
        [3, 4, 5, 180, 6, 7]
    ])
    
    y = ['casual', 'business', 'evening']
    
    # Create and save encoders
    encoders = {
        'skin_tone': LabelEncoder(),
        'style': LabelEncoder(),
        'body_shape': LabelEncoder(),
        'size': LabelEncoder(),
        'gender': LabelEncoder()
    }
    
    # Save encoders
    joblib.dump(encoders, 'model/encoders.joblib')
    
    # Create and save label encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(y)
    joblib.dump(label_encoder, 'model/label_encoder.joblib')
    
    # Create and save initial model
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, label_encoder.transform(y))
    joblib.dump(model, 'model/model.joblib')

# Call this function once to create initial model
create_initial_model()
