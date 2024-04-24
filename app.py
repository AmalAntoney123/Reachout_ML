from flask import Flask, render_template,session, redirect, url_for
from register import register_bp
from login import login_bp

app = Flask(__name__)

app.register_blueprint(register_bp)
app.register_blueprint(login_bp)

app.secret_key = 'secret_key123'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin')
def signin():
    message = session.pop('message', None)
    error = session.pop('error', None)
    # Render the signin template with the success message
    return render_template('signin.html', message=message,error=error)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/template')
def template():
    return render_template('template.html')

@app.route('/user')
def user():
    userName = session.get('name')
    userEmail = session.get('email')
    userAge = session.get('age')
    
    # Check if session variables exist
    if not userName or not userEmail or not userAge:
        # Redirect user to sign-in page if session doesn't exist
        return redirect(url_for('signin'))  # Assuming your sign-in route is named 'signin'

    return render_template('user.html', userEmail=userEmail, userName=userName, userAge = userAge)

@app.route('/logout')
def logout():
    # Clear session data
    session.pop('name', None)
    session.pop('email', None)
    
    # Redirect to the sign-in page
    return redirect(url_for('signin'))  # Assuming your sign-in route is named 'signin'


if __name__ == '__main__':
    app.run(debug=True)