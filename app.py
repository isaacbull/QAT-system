from flask import Flask, jsonify, request, flash, redirect, render_template_string
import os
from werkzeug.utils import secure_filename
import google.generativeai as genai
from utils import query_system_or_return_dummy
from data_models import get_test_question_and_answer
from utils import *
from data_models import *
import uuid
from difflib import SequenceMatcher



app = Flask(__name__)


API_KEY="AIzaSyBpzPj83cCLSlHWNSqX_mFQWbYelerzRpA"

genai.configure(api_key=API_KEY)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def landing_page():
    return render_template_string('''
        <h1>Welcome to the QAT System</h1>
        <p>Click the button below to continue to the uploads page.</p>
        <form action="/upload">
            <input type="submit" value="Continue">
        </form>
    ''')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            original_filename = secure_filename(file.filename)
            extension = original_filename.rsplit('.', 1)[1].lower()
            new_filename = f"file_for_query.{extension}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            return jsonify({"message": "File uploaded successfully", "filename": new_filename}), 201
    return '''
    <!doctype html>
    <title>Upload Research Document</title>
    <h1>Upload Research Document</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/query', methods=['GET','POST'])
def query():
    if request.method == 'POST':
        # Get the question from the form
        user_question = request.form['user_question']
        response = query_system(user_question)

        json_data = extract_json_from_string(response)

        test_question_id = str(uuid.uuid4())  # Generate a unique ID for the test question

        json_data['test_question_id'] = test_question_id

        if 'test_question_id' in json_data:
            save_test_question_id(json_data['test_question_id'])
        database = "responses.db"

        conn = create_connection(database)

        # Create tables
        if conn is not None:
            create_table(conn, sql_create_responses_table)
        else:
            print("Error! Cannot create the database connection.")

        # Insert data into the database
        with conn:
            response_id = insert_data(conn, json_data)
            print("Response inserted with id:", response_id)
        response = {
            "answer": json_data["answer"],
            "bullet_points": json_data["bullet_points"],
            "test_question": json_data["test_question"],
            "test_question_id": json_data["test_question_id"],
        }

        return jsonify(response), 200
    return f'''
        <form action="/query" method="post">
            <label for="user_question">Enter your question:</label><br>
            <input type="text" id="user_question" name="user_question"><br><br>
            <input type="submit" value="Submit">
        </form>
    '''


@app.route('/evaluate', methods=['GET','POST'])
def evaluate():
    question, correct_answer = get_test_question_and_answer()

    if request.method == 'POST':
        user_answer = request.form['answer']
        ratio = SequenceMatcher(None, user_answer, correct_answer).ratio() * 100

        knowledge_understood = ratio > 60
        knowledge_confidence = ratio
        
        # JSON response
        response = {
            "knowledge_understood": knowledge_understood,
            "knowledge_confidence": knowledge_confidence
        }
        
        return (f'<p>Knowledge confidence: {knowledge_confidence}%</p>'
                f'<p>Knowledge Understood: {knowledge_understood}</p>'
                f'<p>Correct Answer: {correct_answer}</p>'
                f'<a href="/evaluate">Try Again</a>'
                f'<pre>{jsonify(response).get_data(as_text=True)}</pre>')
    
    return f'''
        <form action="/evaluate" method="post">
            <label for="question">Question: {question}</label><br>
            <input type="text" id="answer" name="answer"><br><br>
            <input type="submit" value="Submit">
        </form>
    '''






if __name__ == "__main__":
    app.run(debug=True)