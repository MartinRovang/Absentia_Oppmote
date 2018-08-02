from flask import Flask, flash, redirect, render_template, request, session, abort, make_response, send_file, jsonify, Response
from threading import Lock, Timer
import pandas as pd
import numpy as np
import sqlite3 as sql
import sys,os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Unicode, UnicodeText
from sqlalchemy import create_engine, ForeignKey

from wtforms import Form, BooleanField, StringField, PasswordField, validators



sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))
engine = create_engine('sqlite:///twitter.db', echo=True)
Session = sessionmaker(bind=engine)



app = Flask(__name__)



def movingavarage(values,window):
	weights = np.repeat(1.0,window)/window
	smas = np.convolve(values,weights,'valid')
	return smas




class RegistrationForm(Form):
    username = StringField('Ditt Navn', [validators.Length(min=4, max=25)])




@app.route('/')
def home():
    try:
        total_visits = []
        conn = sql.connect("temp.db")
        df_users = pd.read_sql("SELECT * FROM users ", conn)
        users_defined = df_users['name']
        number = df_users['number'].values
        intedlist = [int(i) for i in number]
        winner_number = max(intedlist)
        winner_number_student_search = pd.read_sql("SELECT * FROM users WHERE (number LIKE '%{}%') ".format(winner_number), conn)
        winner_number_student = winner_number_student_search.values[0][1]
        conn.close()
        conn = sql.connect("real.db")
        for i in users_defined:
            df_total_visits = pd.read_sql("SELECT * FROM users WHERE (name LIKE '{}') ".format(i), conn)
            total_visits.append(len(df_total_visits['name']))
        conn.close()
        return render_template('home.html', tripple = zip(users_defined, number, total_visits), winner = winner_number_student)
    except:
        return render_template('home.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        conn = sql.connect('temp.db')
        c = conn.cursor()
        df_users = pd.read_sql("SELECT * FROM users", conn)
        random_number = int(np.random.randint(0,300,1))
        print(random_number)
        form.username.data = str.lower(str(form.username.data))
        try:
            if form.username.data in df_users['name'].values:
                return("UGYLDIG, DOBBELT NAVN")
        except:
            pass
        else:
            c.execute("INSERT INTO users (name, number) VALUES (?,?)", (form.username.data, str(random_number),))
            conn.commit()
            conn.close()
            conn = sql.connect('real.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (name) VALUES (?)", (form.username.data,))
            conn.commit()
            conn.close()
            return render_template('register.html', form = form, takk = 'Takk!, LotteriID: %d'%random_number)

    return render_template('register.html', form=form)



@app.route('/admin')
def admin():
    try:
        total_visits = []
        conn = sql.connect("real.db")
        df_users = pd.read_sql("SELECT * FROM users ", conn)
        users_defined = df_users['name']
        for i in users_defined:
            df_total_visits = pd.read_sql("SELECT * FROM users WHERE (name LIKE '{}') ".format(i), conn)
            total_visits.append(len(df_total_visits['name']))
        conn.close()
        return render_template('admin.html', tripple = zip(users_defined, total_visits))
    except:
        return "Error!"



# thread = threading.Thread(target=foo)
# thread.start()




 
if __name__ == "__main__":

    app.run()


