import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Ensure the model directory exists
os.makedirs('model', exist_ok=True)

# 1) Load dataset
df = pd.read_csv('ml_model/outfit_data.csv')

# 2) Encode categorical input features
encoders = {}
for feat in ['skin_tone', 'style', 'body_shape', 'size']:
    le = LabelEncoder()
    df[feat] = le.fit_transform(df[feat])
    encoders[feat] = le

# 3) Encode the output label
label_encoder = LabelEncoder()
df['outfit_label_enc'] = label_encoder.fit_transform(df['outfit_label'])

# 4) Save encoders
joblib.dump(encoders, 'model/encoders.joblib')
joblib.dump(label_encoder, 'model/label_encoder.joblib')

# 5) Prepare features and labels
X = df[['skin_tone', 'style', 'body_shape', 'height', 'size']]
y = df['outfit_label_enc']

# 6) Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 7) Save model
joblib.dump(model, 'model/model.joblib')

print("Model trained and saved to 'model/' directory.")

# import pandas as pd
# from sklearn.preprocessing import LabelEncoder
# from sklearn.ensemble import RandomForestClassifier
# import joblib, os
#
# # ensure model folder
# os.makedirs('model', exist_ok=True)
#
# # 1) Load the full dataset
# df = pd.read_csv('ml_model/outfit_data.csv')
#
# # 2) Encode features
# encoders = {}
# for feat in ['skin_tone','style','body_shape','size']:
#     le = LabelEncoder()
#     df[feat] = le.fit_transform(df[feat])
#     encoders[feat] = le
#
# # 3) Encode the outfit_label
# label_enc = LabelEncoder()
# df['outfit_label_enc'] = label_enc.fit_transform(df['outfit_label'])
#
# # 4) Save encoders
# joblib.dump(encoders, 'model/encoders.joblib')
# joblib.dump(label_enc, 'model/label_encoder.joblib')
#
# # 5) Train/test split (optional) or train on all
# X = df[['skin_tone','style','body_shape','height','size']]
# y = df['outfit_label_enc']
# model = RandomForestClassifier(n_estimators=100, random_state=42)
# model.fit(X, y)
#
# # 6) Save the model
# joblib.dump(model, 'model/model.joblib')
# print("Model trained and saved.")
