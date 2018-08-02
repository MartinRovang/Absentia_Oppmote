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


def loot():
    magic_number = np.random.randint(0,10,1)
    if magic_number == 0:
        return 'https://gbf.wiki/images/thumb/a/aa/Cosmic_Sword.png/462px-Cosmic_Sword.png'
    if magic_number == 1:
        return 'https://www.claires.com/dw/image/v2/BBTK_PRD/on/demandware.static/-/Sites-master-catalog/default/dwb3e89841/images/hi-res/55138_1.jpg'
    if magic_number == 2:
        return 'https://www.claires.com/dw/image/v2/BBTK_PRD/on/demandware.static/-/Sites-master-catalog/default/dw88b9b105/images/hi-res/38215_1.jpg'
    if magic_number == 3:
        return 'https://thumbs.dreamstime.com/z/american-legendary-pistol-white-background-military-model-47937475.jpg'
    if magic_number == 4:
        return 'https://cdn-4.jjshouse.com/upimg/jjshouse/s1140/4a/e3/af62d123841b74b7e4bc431e0aec4ae3.jpg'
    if magic_number == 5:
        return 'http://ukonic.com/wp-content/uploads/2017/11/WOW_PALADINE_ROBE_1-1000.jpg'
    if magic_number == 6:
        return 'https://thebitbin.files.wordpress.com/2012/08/boots1.png'
    if magic_number == 7:
        return 'https://cdn-media.sportamore.se/uploads/products/5711176095404_001_7a2b071ce45943269c9b78d04124f2e7.jpg'
    if magic_number == 8:
        return 'http://www.omegaartworks.com/images/omega/490-dragonfly-knife-green-andamp;-blackandamp;-daggers.jpg'
    if magic_number == 9:
        return 'https://www.thinkgeek.com/images/products/zoom/1f1a_kawaii_hooded_unicorn_bathrobe.jpg'
    if magic_number == 10:
        return 'http://www.delonghi.com/Global/recipes/multifry/3_pizza_fresca.jpg'




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
        loot_item = loot()
        return render_template('home.html', tripple = zip(users_defined, number, total_visits), winner = winner_number_student, loot_item = loot_item)
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


