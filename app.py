from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from dotenv import load_dotenv
import openai
import os
import base64
from models import db, User, Child
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from models import Drawing 




load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///littlemind.db'
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login failed. Check email/password.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/add-child', methods=['GET', 'POST'])
@login_required
def add_child():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        new_child = Child(name=name, age=age, parent=current_user)
        db.session.add(new_child)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_child.html')

@app.route('/child/<int:child_id>/analyze', methods=['GET', 'POST'])
@login_required
def analyze_child(child_id):
    child = Child.query.filter_by(id=child_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        try:
            file = request.files['drawing']
            image_data = base64.b64encode(file.read()).decode('utf-8')

            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "This is a child's drawing. What emotions or psychological state does it reflect? Please return a one-word emotion at the beginning (like: Happy, Sad, Angry, Anxious, Excited, etc.) followed by a colon, then give a brief explanation."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=500
            )

            result = response.choices[0].message.content.strip()
            if ':' in result:
                mood, explanation = result.split(":", 1)
                mood = mood.strip()
                explanation = explanation.strip()
            else:
                mood = "unknown"
                explanation = result

            drawing = Drawing(
                image_data=image_data,
                result=explanation,
                mood=mood,
                child_id=child.id
            )
            db.session.add(drawing)
            db.session.commit()

            return jsonify({'result': f"{mood}: {explanation}"})

        except Exception as e:
            print("Error analyzing drawing:", e)
            return jsonify({'error': 'Something went wrong during analysis.'}), 500

    return render_template('analyze_child.html', child=child)


@app.route('/child/<int:child_id>/gallery')
@login_required
def child_gallery(child_id):
    child = Child.query.filter_by(id=child_id, user_id=current_user.id).first_or_404()
    drawings = child.drawings  # from backref='drawings'
    
    return render_template('child_gallery.html', child=child, drawings=drawings)

@app.route('/child/<int:child_id>/insight')
@login_required
def child_insight(child_id):
    child = Child.query.filter_by(id=child_id, user_id=current_user.id).first_or_404()
    drawings = child.drawings

    # Extract emotion keywords using simple word matching
    from collections import Counter
    emotion_keywords = ['happy', 'sad', 'angry', 'excited', 'anxious', 'calm', 'confused']
    emotion_counts = Counter()

    timeline = []

    for d in drawings:
        mood = (d.mood or "unknown").lower()
        emotion_counts[mood] += 1
        timeline.append({
        'date': d.timestamp.strftime('%Y-%m-%d'),
        'mood': mood,
        'text': d.result
    })



    return render_template('child_insight.html',drawing=d, child=child,
                           emotion_counts=emotion_counts, timeline=timeline)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

