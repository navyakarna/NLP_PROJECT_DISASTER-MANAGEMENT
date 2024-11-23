# -*- coding: utf-8 -*-
"""Untitled39.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DaMeASKPYx8lx6XtGb9PM4pD1fKozJh9
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset

# Load the cleaned dataset
df = pd.read_csv("cleaned_news_data.csv")

# Example: Use TITLE for classification and CATEGORY as labels
df = df.dropna(subset=["TITLE", "CATEGORY"])  # Drop rows with missing titles or labels
texts = df["TITLE"].tolist()
labels = pd.factorize(df["CATEGORY"])[0]  # Convert categories to numerical labels
label_mapping = dict(enumerate(pd.factorize(df["CATEGORY"])[1]))  # Mapping numerical labels to categories

# Split into train and test sets
train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Load the BERT tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Tokenize the dataset
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
test_encodings = tokenizer(test_texts, truncation=True, padding=True, max_length=128)

# Create a PyTorch Dataset
class NewsDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

train_dataset = NewsDataset(train_encodings, train_labels)
test_dataset = NewsDataset(test_encodings, test_labels)

# Load the BERT model for classification
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(set(labels)))

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",          # Output directory
    num_train_epochs=3,              # Number of epochs
    per_device_train_batch_size=16,  # Batch size for training
    per_device_eval_batch_size=16,   # Batch size for evaluation
    warmup_steps=500,                # Number of warmup steps
    weight_decay=0.01,               # Strength of weight decay
    logging_dir="./logs",            # Directory for logs
    logging_steps=10,
    evaluation_strategy="epoch"
)

# Create a Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

# Train the model
trainer.train()

# Evaluate the model
predictions = trainer.predict(test_dataset)
pred_labels = predictions.predictions.argmax(axis=1)

# Print classification report
print("Classification Report:")
# Ensure labels and target names match the dataset
unique_labels = sorted(set(test_labels))
target_names = [label_mapping[label] for label in unique_labels]

# Generate classification report
print(classification_report(
    test_labels,
    pred_labels,
    labels=unique_labels,
    target_names=target_names,
    zero_division=0  # Handle cases where predictions are missing for some classes
))

!pip install googlemaps
import spacy
import pandas as pd
import googlemaps

# Load SpaCy's pre-trained model
nlp = spacy.load("en_core_web_sm")

# Initialize Google Maps client with your API key
gmaps = googlemaps.Client(key="YOUR_GOOGLE_MAPS_API_KEY")

# Function to extract locations using NER
def extract_locations(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # GPE = Geo-political entity (e.g., cities, countries)
    return locations

# Function to geocode a location
def geocode_location(location):
    try:
        geocode_result = gmaps.geocode(location)
        if geocode_result:
            lat = geocode_result[0]["geometry"]["location"]["lat"]
            lng = geocode_result[0]["geometry"]["location"]["lng"]
            return lat, lng
    except Exception as e:
        print(f"Error geocoding location '{location}': {e}")
    return None, None

# Load cleaned data
df = pd.read_csv("cleaned_news_data.csv")

# Extract locations and geocode them
location_data = []

for index, row in df.iterrows():
    title = row["TITLE"] if "TITLE" in row else ""
    description = row["DESCRIPTION"] if "DESCRIPTION" in row else ""
    text = f"{title} {description}"  # Combine title and description for location extraction

    # Extract locations
    locations = extract_locations(text)

    # Geocode locations
    for loc in locations:
        lat, lng = geocode_location(loc)
        location_data.append({"Original Text": text, "Location": loc, "Latitude": lat, "Longitude": lng})

# Convert location data to a DataFrame
location_df = pd.DataFrame(location_data)

# Save the results
location_df.to_csv("/mnt/data/location_geotagging_results.csv", index=False)
print("Geotagging completed. Results saved to 'location_geotagging_results.csv'.")

!pip install opencage
import spacy
import pandas as pd
from opencage.geocoder import OpenCageGeocode

# Load SpaCy's pre-trained model
nlp = spacy.load("en_core_web_sm")

# Initialize OpenCage Geocoder with your API key
key = "bf1410ec5fbf4ce6a0d040cd49cca523"  # Replace with your OpenCage API key
geocoder = OpenCageGeocode(key)

# Function to extract locations using NER
def extract_locations(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # GPE = Geo-political entity (e.g., cities, countries)
    return locations

# Function to geocode a location
def geocode_location(location):
    try:
        results = geocoder.geocode(location)
        if results:
            lat = results[0]["geometry"]["lat"]
            lng = results[0]["geometry"]["lng"]
            return lat, lng
    except Exception as e:
        print(f"Error geocoding location '{location}': {e}")
    return None, None

# Load cleaned data
df = pd.read_csv("cleaned_news_data.csv")

# Extract locations and geocode them
location_data = []

for index, row in df.iterrows():
    title = row["TITLE"] if "TITLE" in row else ""
    description = row["DESCRIPTION"] if "DESCRIPTION" in row else ""
    text = f"{title} {description}"  # Combine title and description for location extraction

    # Extract locations
    locations = extract_locations(text)

    # Geocode locations
    for loc in locations:
        lat, lng = geocode_location(loc)
        location_data.append({"Original Text": text, "Location": loc, "Latitude": lat, "Longitude": lng})

# Convert location data to a DataFrame
location_df = pd.DataFrame(location_data)

# Save the results
for data in location_data:
    print(f"Original Text: {data['Original Text']}")
    print(f"Location: {data['Location']}")
    print(f"Latitude: {data['Latitude']}, Longitude: {data['Longitude']}")
    print('-' * 50)

!pip install twilio
import pandas as pd
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Example function to classify and send an alert
def send_alert(message, alert_type, severity):
    # Alert system: severity threshold for sending alerts
    if severity >= 0.7:
        if alert_type == 'sms':
            send_sms_alert(message)
        elif alert_type == 'email':
            send_email_alert(message)

# Function to send SMS via Twilio
def send_sms_alert(message):
    # Twilio API credentials
    account_sid = 'AC4ed9110460a589b48ca55f87a410622f'
auth_token = '[AuthToken]'
client = Client(account_sid, auth_token)
message = client.messages.create(
  messaging_service_sid='MGc2a10f9df1071c9f04082e643574550d',
  body='Ahoy 👋',
  to='+18777804236'
)

print(message.sid)

# Function to send an email alert
def send_email_alert(message):
    # Email configuration
    sender_email = "navya21csu185@ncuindia.edu"
    receiver_email = "navyakarnas309@gmail.com"
    password = "21csu185"  # Use app-specific password for Gmail

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Disaster Alert"

    body = MIMEText(message, 'plain')
    msg.attach(body)

    # Send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("Email sent.")

# Example trigger
message = "Flood warning in Mumbai, India. Immediate evacuation advised!"
send_alert(message, alert_type='sms', severity=0.9)  # Send SMS if severity is high

!pip install dash
import spacy
import pandas as pd
from opencage.geocoder import OpenCageGeocode
from twilio.rest import Client
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

# SpaCy's pre-trained model for NER
nlp = spacy.load("en_core_web_sm")

# Initialize OpenCage Geocoder with your API key (replace with your OpenCage API key)
key = "bf1410ec5fbf4ce6a0d040cd49cca523"
geocoder = OpenCageGeocode(key)

# Twilio API credentials for SMS
account_sid = 'AC4ed9110460a589b48ca55f87a410622f'  # Replace with your Twilio SID
auth_token = 'YOUR_AUTH_TOKEN'  # Replace with your Twilio Auth Token
client = Client(account_sid, auth_token)

# Function to extract locations using NER
def extract_locations(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # GPE = Geo-political entity (e.g., cities, countries)
    return locations

# Function to geocode a location
def geocode_location(location):
    try:
        results = geocoder.geocode(location)
        if results:
            lat = results[0]["geometry"]["lat"]
            lng = results[0]["geometry"]["lng"]
            return lat, lng
    except Exception as e:
        print(f"Error geocoding location '{location}': {e}")
    return None, None

# Function to send SMS alert via Twilio
def send_sms_alert(message):
   account_sid = 'AC4ed9110460a589b48ca55f87a410622f'
auth_token = '667ef1fdafbe04b865ddf4b4caaea4a1'
client = Client(account_sid, auth_token)
message = client.messages.create(
  messaging_service_sid='MGc2a10f9df1071c9f04082e643574550d',
  body='Disaster Alert: Earthquake or flood expected',
  to='+918826522347'
)
print(message.sid)

# Example function to classify and send an alert based on severity
def send_alert(message, alert_type, severity):
    # Severity threshold (e.g., severity >= 0.7 triggers an alert)
    if severity >= 0.7:
        if alert_type == 'sms':
            send_sms_alert(message)
        elif alert_type == 'email':
            send_email_alert(message)

# Example email function (this could be added to your email system)
def send_email_alert(message):
    # Email sending logic (you can modify with your email credentials)
    print(f"Email alert sent: {message}")

# Load and clean your dataset (replace with actual CSV path)
df = pd.read_csv("cleaned_news_data.csv")


if 'CATEGORY' in df.columns:
    df = df.rename(columns={'CATEGORY': 'Disaster Type'})
else:
    # If 'CATEGORY' column is not found, create 'Disaster Type' column
    # and assign a default value (e.g., 'Unknown') to all rows
    df['Disaster Type'] = 'Unknown'




# Extract locations and geocode them
location_data = []

for index, row in df.iterrows():
    title = row["TITLE"] if "TITLE" in row else ""
    description = row["DESCRIPTION"] if "DESCRIPTION" in row else ""
    text = f"{title} {description}"  # Combine title and description for location extraction

    # Extract locations
    locations = extract_locations(text)

    # Geocode locations
    for loc in locations:
        lat, lng = geocode_location(loc)
        location_data.append({"Original Text": text, "Location": loc, "Latitude": lat, "Longitude": lng})

# Display the results and send alerts (for testing purposes)
for data in location_data:
    print(f"Original Text: {data['Original Text']}")
    print(f"Location: {data['Location']}")
    print(f"Latitude: {data['Latitude']}, Longitude: {data['Longitude']}")

    # Example severity (for testing): If sentiment or context indicates urgency, send an alert
    send_alert("Flood warning in Mumbai, India. Immediate evacuation advised!", 'sms', severity=0.9)

# Dash App for visualization
app = dash.Dash(__name__)

# Layout for the Dash app
app.layout = html.Div([
    html.H1("Real-time Disaster Monitoring Dashboard"),
    dcc.Dropdown(
        id='disaster_type',
        options=[{'label': x, 'value': x} for x in df['Disaster Type'].unique()],
        value='Flood',  # Default value
        style={'width': '50%'}
    ),
    dcc.Graph(id='map', style={'height': '600px'})
])

# Callback to update map based on selected disaster type
@app.callback(
    Output('map', 'figure'),
    Input('disaster_type', 'value')
)
def update_map(disaster_type):
    filtered_df = df[df['Disaster Type'] == disaster_type]

    fig = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Location",
        color="Severity",
        size="Severity",
        size_max=15,
        color_continuous_scale="Viridis",
        title=f"Disasters: {disaster_type}",
        mapbox_style="carto-positron"
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)