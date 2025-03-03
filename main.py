import os
import re
import openai
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI", "")
OPENROUTER_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")  # or "OPENROUTER_API_KEY"

# Configure MongoDB
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["sample_database"]
collection = db["pgagi"]

app = Flask(__name__)
app.secret_key = 'some_random_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# ---------------------------------------------------------
# 1) Configure the openai library for OpenRouter
# ---------------------------------------------------------
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"  # The base URL for openrouter

def validate_with_deepseek(user_input, field_type):
    """
    Validate user input for a specific field type using the DeepSeek model
    on OpenRouter. Must respond STRICTLY with "VALID" or "INVALID".
    """
    system_content = (
        "You are a strict validator for user input fields.\n\n"
        "Rules:\n"
        "- Respond ONLY with 'VALID' or 'INVALID' (uppercase, no extra words).\n"
        "- Full Name: At least two words, primarily alphabetic.\n"
        "- Email Address: Must have '@' and a domain extension like .com, etc.\n"
        "- Phone Number: Mostly digits (+, -, spaces), at least 7 digits.\n"
        "- Years of Experience: Integer 0-60.\n"
        "- Desired Position: At least 2 letters.\n"
        "- Current Location: At least 2 letters.\n"
        "- Tech Stack: Non-empty, at least 2 letters.\n"
    )

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Field Type: {field_type}\nUser Input: {user_input}"}
    ]

    try:
        # Call openai.ChatCompletion.create with your model
        completion = openai.ChatCompletion.create(
            model="deepseek/deepseek-r1:free",
            messages=messages,
            # Optional request headers for analytics on openrouter.ai
            # => Not supported directly in create(...).
            # If needed, you can do a requests.post approach instead.
        )
        if completion.choices:
            text_out = completion.choices[0].message["content"].strip().upper()
            return (text_out == "VALID")
        else:
            return False
    except Exception as e:
        print("DeepSeek validation error:", e)
        return False

@app.route('/')
def index():
    # Clear session on page load
    session.clear()
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'stage' not in session:
        session['stage'] = 0
        session['candidate_data'] = {}

    user_message = request.json.get('message', '').strip()
    stage = session['stage']
    candidate_data = session['candidate_data']

    # End conversation keywords
    if user_message.lower() in ['exit', 'quit', 'bye']:
        session.clear()
        return jsonify({'bot_message': "Thank you for using TalentScout Hiring Assistant. Goodbye!"})

    # Conversation flow
    if stage == 0:
        session['stage'] = 1
        return jsonify({
            'bot_message': (
                "Hello! Welcome to TalentScout's Hiring Assistant chatbot. "
                "I'm here to help with the initial screening process. "
                "Let's begin.\n\nWhat is your full name?"
            )
        })

    elif stage == 1:
        if validate_with_deepseek(user_message, "full name"):
            candidate_data['full_name'] = user_message
            session['stage'] = 2
            return jsonify({'bot_message': "Great! What's your email address?"})
        else:
            return jsonify({'bot_message': "That doesn't look like a valid full name. Please try again."})

    elif stage == 2:
        sanitized_email = re.sub(r'[<>]', '', user_message.strip())
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(email_regex, sanitized_email):
            if validate_with_deepseek(sanitized_email, "email address"):
                candidate_data['email'] = sanitized_email
                session['stage'] = 3
                return jsonify({'bot_message': "Thanks! What's your phone number?"})
            else:
                return jsonify({'bot_message': "That doesn't look like a valid email address. Please try again."})
        else:
            return jsonify({'bot_message': "That doesn't look like a valid email address. Please try again."})

    elif stage == 3:
        if validate_with_deepseek(user_message, "phone number"):
            candidate_data['phone'] = user_message
            session['stage'] = 4
            return jsonify({'bot_message': "Got it. How many years of experience do you have?"})
        else:
            return jsonify({'bot_message': "That doesn't look like a valid phone number. Please try again."})

    elif stage == 4:
        try:
            years = int(user_message)
            if 0 <= years <= 50:
                if validate_with_deepseek(user_message, "years of experience"):
                    candidate_data['years_exp'] = user_message
                    session['stage'] = 5
                    return jsonify({'bot_message': "Understood. What is your desired position(s)?"})
                else:
                    return jsonify({'bot_message': "That doesn't look like a valid response for years of experience. Please try again."})
            else:
                return jsonify({'bot_message': "Years of experience must be between 0 and 50. Please try again."})
        except ValueError:
            return jsonify({'bot_message': "That doesn't look like a valid integer. Please try again."})

    elif stage == 5:
        if validate_with_deepseek(user_message, "desired position"):
            candidate_data['desired_positions'] = user_message
            session['stage'] = 6
            return jsonify({'bot_message': "Thank you. What's your current location?"})
        else:
            return jsonify({'bot_message': "That doesn't look like a valid desired position. Please try again."})

    elif stage == 6:
        if validate_with_deepseek(user_message, "current location"):
            candidate_data['current_location'] = user_message
            session['stage'] = 7
            return jsonify({'bot_message': "Great! Please list your tech stack (e.g., Python, Django, SQL)."})
        else:
            return jsonify({'bot_message': "That doesn't look like a valid location. Please try again."})

    elif stage == 7:
        # Validate tech stack
        if validate_with_deepseek(user_message, "tech stack"):
            candidate_data['tech_stack'] = user_message
    
            # Force the model to produce exactly 3 lines labeled Q1:, Q2:, Q3:
            system_msg = {
                "role": "system",
                "content": (
                    "You are an interviewer creating exactly 3 short, beginner-level questions. "
                    "Each question must begin with 'Q1:', 'Q2:', or 'Q3:' and then a brief question. "
                    "No extra lines, no disclaimers, no repeated numbering. "
                    "Keep each question short (max 2 lines)."
                )
            }
            user_msg = {
                "role": "user",
                "content": f"The tech stack is: {user_message}"
            }
    
            try:
                completion = openai.ChatCompletion.create(
                    model="deepseek/deepseek-r1:free",
                    messages=[system_msg, user_msg]
                )
                if completion.choices:
                    questions_text = completion.choices[0].message["content"].strip()
                else:
                    questions_text = "No questions generated."
    
                # Split by lines, ignoring empties
                lines = [line.strip() for line in questions_text.split('\n') if line.strip()]
    
                # Post-process lines to unify or remove extraneous text
                questions_list = []
                for line in lines:
                    # If the line starts with "Q1:", "Q2:", or "Q3:", keep it
                    lower_line = line.lower()
                    if lower_line.startswith("q1:"):
                        # Remove "q1:" prefix and unify format
                        question = line[3:].strip()
                        questions_list.append(f"Q1: {question}")
                    elif lower_line.startswith("q2:"):
                        question = line[3:].strip()
                        questions_list.append(f"Q2: {question}")
                    elif lower_line.startswith("q3:"):
                        question = line[3:].strip()
                        questions_list.append(f"Q3: {question}")
    
                # If the model gave us fewer than 3 lines, or none at all, handle that
                if len(questions_list) < 3:
                    # Optionally fill them with placeholders or skip
                    pass
    
                session['tech_questions_list'] = questions_list
                session['answers'] = []
                session['current_q_index'] = 0
    
                session['stage'] = 8
                if questions_list:
                    first_question = questions_list[0]
                    return jsonify({
                        'bot_message': (
                            "Thanks! Let's go through your tech questions.\n\n"
                            f"Question 1: {first_question}"
                        )
                    })
                else:
                    session['stage'] = 11
                    return jsonify({'bot_message': "No questions generated. Type 'exit' to end."})
    
            except Exception as e:
                print("DeepSeek generation error:", e)
                return jsonify({
                    'bot_message': "Oops, there was an error generating questions. "
                                   "Please try again or type 'exit' to end."
                })
        else:
            return jsonify({'bot_message': "That doesn't look like a valid tech stack. Please try again."})


    elif stage == 8:
        answers = session.get('answers', [])
        answers.append(user_message)
        session['answers'] = answers

        questions_list = session.get('tech_questions_list', [])
        session['current_q_index'] = 1
        session['stage'] = 9

        if len(questions_list) > 1:
            return jsonify({'bot_message': f"Question 2: {questions_list[1]}"})
        else:
            session['stage'] = 11
            return jsonify({'bot_message': "No more questions. Type 'exit' to end."})

    elif stage == 9:
        answers = session.get('answers', [])
        answers.append(user_message)
        session['answers'] = answers

        questions_list = session.get('tech_questions_list', [])
        session['current_q_index'] = 2
        session['stage'] = 10

        if len(questions_list) > 2:
            return jsonify({'bot_message': f"Question 3: {questions_list[2]}"})
        else:
            session['stage'] = 11
            return jsonify({'bot_message': "No more questions. Type 'exit' to end."})

    elif stage == 10:
        answers = session.get('answers', [])
        answers.append(user_message)
        session['answers'] = answers

        session['stage'] = 11
        return jsonify({'bot_message': "Thanks for your answers! Type 'done' to finalize or 'exit' to quit."})

    elif stage == 11:
        if user_message.lower() == 'done':
            candidate_data['answers'] = session.get('answers', [])
            candidate_data['questions'] = session.get('tech_questions_list', [])

            collection.insert_one({
                "full_name": candidate_data.get('full_name'),
                "email": candidate_data.get('email'),
                "phone": candidate_data.get('phone'),
                "years_exp": candidate_data.get('years_exp'),
                "desired_positions": candidate_data.get('desired_positions'),
                "current_location": candidate_data.get('current_location'),
                "tech_stack": candidate_data.get('tech_stack'),
                "questions": candidate_data.get('questions'),
                "answers": candidate_data.get('answers')
            })

            session['stage'] = 12
            return jsonify({'bot_message': "All data saved! Thank you. Type 'exit' to leave or continue chatting."})
        else:
            return jsonify({'bot_message': "Type 'done' to finalize or 'exit' to quit."})

    else:
        return jsonify({'bot_message': "We've already saved your data. Type 'exit' to end."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
