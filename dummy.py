from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib

# Load the dataset
file_path =  r"C:\Users\namei\Downloads\cleaned_tags_fixed.csv"
data = pd.read_csv(file_path)

# Preprocessing for ML
vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")  # Extract features
X = vectorizer.fit_transform(data['tweet'])  # Transform the tweet column into feature vectors

# Train a NearestNeighbors model
model = NearestNeighbors(n_neighbors=20, metric="cosine")  # Cosine similarity
model.fit(X)

# Save vectorizer and model for reusability
joblib.dump(vectorizer, "vectorizer.pkl")
joblib.dump(model, "knn_model.pkl")

# Flask app
app = Flask(__name__)
app.secret_key = "super_secret_key"  # Secret key for session management

# Mock database
users = {}

# Dummy user credentials
USER_CREDENTIALS = {"admin": "password123", "user": "user123"}

# HTML Templates
login_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
      <img src=r"C:\\Users\\kanna\OneDrive\\Desktop\\gif.gif" width="200">

    <style>
       body {
    font-family: Arial, sans-serif;
    background-image: url('https://cdn.dribbble.com/users/2333195/screenshots/5317016/media/07017d669d4df2bdb901ed8a4bee9697.gif'); 
    background-repeat: no-repeat;
    margin: 0;
    padding:350px 0px 0px 0px;
    background-size: cover;
    background-position: center;
}

        .container { 
          max-width: 400px;
          margin: 50px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; }
        button { width: 100%; padding: 10px; background:#FFA4C1; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #B97E91; }
        a { display: block; text-align: center; margin-top: 10px; color: #4caf50; text-decoration: none; }
        .container {
    background-color: rgba(255, 255, 255, 0.5); /* Transparent white */
    padding: 20px;
    border-radius: 10px;
    width: 300px;
    margin: auto;
    text-align: center;
  }

  input, button {
    display: block;
    margin: 10px auto;
    padding: 10px;
    width: 90%;
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        <form method="post" action="/login">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <button ,type="submit">Login</button>
        </form>
        <a href="/signup" style="color: #B15E78; font-weight: bold;">Don't have an account? Signup</a>

    </div>
</body>
</html>


"""

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Hashtag Prediction</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(to right, #4caf50, #81c784);
            background-image: url('https://cdn.dribbble.com/users/2333195/screenshots/5317016/media/07017d669d4df2bdb901ed8a4bee9697.gif'); 
            background-size: cover; 
            background-position: center; 
            background-repeat: no-repeat; 
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: #fff;
            color: #333;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            background-color: rgba(255, 255, 255, 0.5);
            width: 500px;
        }
        h1 {
            text-align: center;
            color:#17A3AA;
        }
        form {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input {
            width: calc(100% - 20px);
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            width: 100%;
            padding: 10px;
            background:#D87796;
            color:black;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            background: #E53E73;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background: white;
            margin: 5px 0;
            padding: 10px;
            border-radius: 5px;
            color: #333;
        }
        .error {
            text-align: center;
            color: red;
            font-weight: bold;
        }
        .slist {
    max-height: 200px;
    overflow-y: auto; 
    padding-right: 10px;
    list-style-type: none;
}
    </style>
</head>
<body>
    <div class="container">
        <h1>Hashtag Prediction</h1>
        <form method="post" action="/">
            <label for="word">Enter Karo Get Karoo:</label>
            <input type="text" id="word" name="word" required>
            <button type="submit">Predict</button>
        </form>
           <hr>
    {% if related_hashtags %}
        <h2>Trending Tags:</h2>
        <ul class="slist">
        {% for hashtag in related_hashtags %}
            <li>{{ hashtag }}</li>
        {% endfor %}
        </ul >
    {% elif error %}
        <h2 class="error">{{ error }}</h2>
    {% endif %}
    <form method="get" action="/logout">
            <button type="submit" class="logout">Logout</button>
        </form>
    </div>
</body>
</html>
"""

signUp_template="""
<!DOCTYPE html>
<html>
<head>
    <title>Signup</title>
    <style>
        body {
          font-family: Arial, sans-serif;
          background-image: url('https://cdn.dribbble.com/users/2333195/screenshots/5317016/media/07017d669d4df2bdb901ed8a4bee9697.gif'); 
          background-repeat: no-repeat;
          margin: 0;
         padding:100px 0px 0px 0px;
        background-size: cover;
        background-position: center;
           }
        .container
          {
          max-width: 400px;
         margin: 50px auto;
         padding: 20px; 
         background: transparent;
         border-radius: 10px; 
         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
           }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #FFA4C1; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #B15E78; }
        a { display: block; text-align: center; margin-top: 10px; color: #4caf50; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Signup</h2>
        <form method="post" action="/signup">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
            <button type="submit">Signup</button>
        </form>
        
         <a href="/login" style="color: #B15E78; font-weight: bold;">Already have an account? Login</a>
    </div>
</body>
</html>

"""

# Helper function to predict hashtags
# Helper function to predict hashtags
def predict_hashtags(input_text):
    # Load vectorizer and model
    vectorizer = joblib.load("vectorizer.pkl")
    model = joblib.load("knn_model.pkl")
    
    # Vectorize input text
    input_vector = vectorizer.transform([input_text])
    
    # Find similar tweets
    distances, indices = model.kneighbors(input_vector)
    
    # Collect hashtags from the nearest neighbors
    nearest_tweets = data.iloc[indices[0]]
    hashtags = nearest_tweets['hashtags'].unique()
    
    if hashtags.size > 0:
        return {"related_hashtags": hashtags.tolist()}
    else:
        return {"error": "No matching hashtags found."}

# Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if username in users:
            return render_template_string(signUp_template, error="Username already exists")
        elif password != confirm_password:
            return render_template_string(signUp_template, error="Passwords do not match")
        else:
            users[username] = password
            return redirect(url_for('login'))

    return render_template_string(signUp_template)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('predict'))
        else:
            return render_template_string(login_template, error="Invalid username or password")

    return render_template_string(login_template)

@app.route('/', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    related_hashtags = None
    error = None

    if request.method == 'POST':
        input_text = request.form.get('word')
        if input_text:
            result = predict_hashtags(input_text)
            related_hashtags = result.get('related_hashtags')
            error = result.get('error')

    return render_template_string(html_template, 
                                   related_hashtags=related_hashtags, 
                                   error=error)
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, port=5432)

