from flask import Blueprint, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
from model import model
import traceback

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommendation', methods=['POST'])
def recommendation():
    try:
        form_data = request.get_json()
        userAge = session.get('age')
        userGender = 1 if session.get('gender') == 'male' else 2

        # Extract the feature values from the form data
        Q1_Stress = form_data.get('stress')
        Q2_Anxiety = form_data.get('anxiety')
        Q3_Depression = form_data.get('depression')
        Q4_Sleep = form_data.get('sleep')
        Q5_Social = form_data.get('social')

        # Store the form data values in the session
        session['stress'] = Q1_Stress
        session['anxiety'] = Q2_Anxiety
        session['depression'] = Q3_Depression
        session['sleep'] = Q4_Sleep
        session['social'] = Q5_Social

        # Create a feature vector
        feature_vector = [[userAge, userGender, Q1_Stress, Q2_Anxiety, Q3_Depression, Q4_Sleep, Q5_Social]]

        # Make a prediction using the trained model
        prediction = model.predict(feature_vector)[0]

        if prediction == "Counseling":
            session['recommendation'] = "You should seek counseling for your well-being."
        elif prediction == "Exercise":
            session['recommendation'] = "You should incorporate regular exercise into your routine."
        elif prediction == "Therapy":
            session['recommendation'] = "You should explore therapy as a potential solution."
        elif prediction == "Mindfulness":
            session['recommendation'] = "You should practice mindfulness techniques to improve your mental state."
        elif prediction == "Support Group":
            session['recommendation'] = "You should join a support group to connect with others in similar situations."
        elif prediction == "Stress Management":
            session['recommendation'] = "You should implement effective stress management strategies."
        elif prediction == "Physical Activity":
            session['recommendation'] = "You should engage in physical activities to boost your overall well-being."
        elif prediction == "Psychotherapy":
            session['recommendation'] = "You should seek psychotherapy to address your concerns."
        elif prediction == "Yoga":
            session['recommendation'] = "You should incorporate yoga into your routine for mental and physical benefits."
        elif prediction == "Social Support":
            session['recommendation'] = "You should seek social support from your loved ones or community."
        elif prediction == "Meditation":
            session['recommendation'] = "You should practice meditation to cultivate mindfulness and inner peace."
        elif prediction == "Life Coach":
            session['recommendation'] = "You should work with a life coach to help you achieve your goals."
        elif prediction == "Group Therapy":
            session['recommendation'] = "You should explore group therapy as a potential solution."
        elif prediction == "Time Management":
            session['recommendation'] = "You should implement effective time management strategies."
        elif prediction == "CBT (Cognitive Behavioral Therapy)":
            session['recommendation'] = "You should try Cognitive Behavioral Therapy (CBT) to address your concerns."
        elif prediction == "Self-Care":
            session['recommendation'] = "You should prioritize self-care practices for your overall well-being."
        else:
            session['recommendation'] = "The recommendation is not recognized."
            

        # Set the session expiration for the current day
        session.permanent = True
        # app.permanent_session_lifetime = timedelta(days=1)

        # Redirect to the /user route
        return redirect(url_for('user'))

    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
    
@recommend_bp.route('/moodReset', methods=['POST','GET'])
def moodReset():
    try:
        session.pop('stress', None)
        session.pop('anxiety', None)
        session.pop('depression', None)
        session.pop('sleep', None)
        session.pop('social', None)
        session.pop('recommendation', None)
        return redirect(url_for('user'))
    except Exception as e:
        print(f'Error resetting session variables: {e}')
        return '', 500
