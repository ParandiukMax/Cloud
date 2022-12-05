from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, session, request
from flask_dance.contrib.google import make_google_blueprint, google
import pymysql

load_dotenv()
app = Flask(__name__)
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
app.secret_key = os.getenv('secret_key')

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"]
)

app.register_blueprint(blueprint, url_prefix="/login")

currentdir = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    google_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'
    if google.authorized:
        google_data = google.get(user_info_endpoint).json()

    now = datetime.now()  # current date and time
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

    return render_template('index.j2',
                           google_data=google_data,
                           fetch_url=google.base_url + user_info_endpoint,
                           date_time=date_time)


# @app.route('/', methods=['POST'])
# def registration():
#     google_data = None
#     user_info_endpoint = '/oauth2/v2/userinfo'
#     google_data = google.get(user_info_endpoint).json()
#
#     now = datetime.now()  # current date and time
#     date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
#
#     # name = request.form[google_data.name]
#     # date = request.form[date_time]
#     name = "google_data.name"
#     date = date_time
#     subject = request.form["Subject"]
#
#     connection = sqlite3.connect("Registration.db")
#     cursor = connection.cursor()
#     # query ="INSERT into Employees (Name, date, subject) values (?,?,?)", (name, date, subject)
#     # query = "INSERT INTO Regist VALUES('{n}', '{d}', '{s})".format(n=name, d=date, s=subject)
#     cursor.execute("INSERT into Regist (Name, date, subject) values (?,?,?)", (name, date, subject))
#     connection.commit()
#     connection.close()
#     return redirect("/")


@app.route('/', methods=['POST'])
def registration():
    now = datetime.now()  # current date and time
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    google_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'
    if google.authorized:
        google_data = google.get(user_info_endpoint).json()

    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    conn = pymysql.connect(user=db_user,
                           password=db_password,
                           unix_socket=unix_socket,
                           db=db_name,
                           cursorclass=pymysql.cursors.DictCursor
                           )
    name = google_data['name']
    date = date_time
    subject = request.form["Subject"]
    with conn.cursor() as cursor:
        cursor.execute(''' INSERT INTO registr2 VALUES(%s,%s,%s)''', (name, date, subject))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route('/login')
def login():
    return redirect(url_for('google.login'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()

