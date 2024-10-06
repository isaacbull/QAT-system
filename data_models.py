import sqlite3
import json




sql_create_responses_table = """ CREATE TABLE IF NOT EXISTS responses (
                                        id integer PRIMARY KEY,
                                        answer text NOT NULL,
                                        bullet_points text,
                                        test_question text,
                                        test_answer text,
                                        test_question_id text
                                    ); """

def create_connection(db_file):
  """Creates a database connection to the SQLite database specified by db_file."""
  conn = None
  try:
    conn = sqlite3.connect(db_file)
    return conn
  except sqlite3.Error as e:
    print(e)
  return conn

def create_table(conn, create_table_sql):
  """Creates a table from the create_table_sql statement."""
  try:
    c = conn.cursor()
    c.execute(create_table_sql)
  except sqlite3.Error as e:
    print(e)

def insert_data(conn, data):
  """Inserts data into the 'responses' table."""
  sql = ''' INSERT INTO responses(answer, bullet_points, test_question, test_answer, test_question_id)
              VALUES(?,?,?,?,?) '''
  cur = conn.cursor()
  cur.execute(sql, (data['answer'], json.dumps(data['bullet_points']), data['test_question'], data['test_answer'], data['test_question_id']))
  conn.commit()
  return cur.lastrowid



def get_test_question_and_answer():
  """Retrieves the test question and answer from the responses table based on the test_question_id in the file."""
  try:
    with open('test_question_id.txt', 'r') as f:
      test_question_id = f.read()

    conn = create_connection("responses.db")
    if conn is not None:
      cur = conn.cursor()
      cur.execute("SELECT test_question, test_answer FROM responses WHERE test_question_id = ?", (test_question_id,))
      row = cur.fetchone()
      if row:
        return row[0], row[1]
      else:
        print("No test question and answer found for the given test_question_id.")
        return None, None
    else:
      print("Error! Cannot create the database connection.")
      return None, None

  except FileNotFoundError:
    print("test_question_id.txt not found, confirm that you have used the prerequisite queries.")
    return None, None

def get_test_question_and_answer_or_dummy():
  try:
    question, answer = get_test_question_and_answer()
    return question, answer
  except Exception as e:
    return "Dummy Question?", "Dummy Answer."
