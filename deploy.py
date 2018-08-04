from flask import Flask, flash, redirect, render_template, request, session, abort, make_response, send_file, jsonify, Response, url_for
from threading import Lock, Timer
import pandas as pd
import numpy as np
import sqlite3 as sql
import sys,os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Unicode, UnicodeText, Date, Integer, String
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import tabledeff
from wtforms import Form, BooleanField, StringField, PasswordField, validators
import string


sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))



app = Flask(__name__)



def movingavarage(values,window):
	weights = np.repeat(1.0,window)/window
	smas = np.convolve(values,weights,'valid')
	return smas

#remove duplicates
def dup_remove(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


class RegistrationForm(Form):
    username = StringField('Ditt Navn', [validators.Length(min=4, max=25)])

class AdminForm(Form):
    password = PasswordField('Passord')


def loot(winner_number):
    link = 0
    print(winner_number)
    if winner_number < 9:
        link =  'https://gbf.wiki/images/thumb/a/aa/Cosmic_Sword.png/462px-Cosmic_Sword.png'
    elif winner_number > 8:
        link = 'https://www.claires.com/dw/image/v2/BBTK_PRD/on/demandware.static/-/Sites-master-catalog/default/dwb3e89841/images/hi-res/55138_1.jpg'
        if winner_number > 19:
            link =  'https://www.claires.com/dw/image/v2/BBTK_PRD/on/demandware.static/-/Sites-master-catalog/default/dw88b9b105/images/hi-res/38215_1.jpg'
            if winner_number > 29:
                link =  'https://thumbs.dreamstime.com/z/american-legendary-pistol-white-background-military-model-47937475.jpg'
                if winner_number > 39:
                    link =  'https://cdn-4.jjshouse.com/upimg/jjshouse/s1140/4a/e3/af62d123841b74b7e4bc431e0aec4ae3.jpg'
                    if winner_number > 49:
                        link =  'http://ukonic.com/wp-content/uploads/2017/11/WOW_PALADINE_ROBE_1-1000.jpg'
                        if winner_number > 59:
                            link =  'https://thebitbin.files.wordpress.com/2012/08/boots1.png'
                            if winner_number > 69:
                                link =  'https://cdn-media.sportamore.se/uploads/products/5711176095404_001_7a2b071ce45943269c9b78d04124f2e7.jpg'
                                if winner_number > 79:
                                    link =  'http://www.omegaartworks.com/images/omega/490-dragonfly-knife-green-andamp;-blackandamp;-daggers.jpg'
                                    if winner_number > 89:
                                        link =  'https://www.thinkgeek.com/images/products/zoom/1f1a_kawaii_hooded_unicorn_bathrobe.jpg'
                                        if winner_number > 98:
                                            link =  'http://www.delonghi.com/Global/recipes/multifry/3_pizza_fresca.jpg'
    else:
        return "Error"
    return link



@app.route('/system/reset')
def reset_day():
    try:
        os.remove('temp.db')
        tabledeff.reset_dayusers()
    except:
        tabledeff.reset_dayusers()
        reset = "Day list have been reset"
        return render_template('home_reset.html', reset = reset) 
    reset = "Day list have been reset"
    return render_template('home_reset.html', reset = reset)


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
        loot_item = loot(winner_number)

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
        random_number = int(np.random.randint(0,100,1))
        print(random_number)
        try:
            form.username.data = string.capwords(str(form.username.data))
            if form.username.data in df_users['name'].values:
                return("UGYLDIG, DOBBELT NAVN")
        except:
            print("ERRRIOR")
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
            name_inserted = form.username.data
            form.username.data = ""
            return render_template('register.html', form = form, takk = '%s registert!, Lotteri-ID: %d'%(name_inserted, random_number))

    return render_template('register.html', form=form)




@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminForm(request.form)
    if request.method == 'POST' and form.validate():
        with open('pws.dat', 'r') as pws:
            if str(pws.read()) == str(form.password.data):
                total_visits = []
                conn = sql.connect("real.db")
                df_users = pd.read_sql("SELECT * FROM users ", conn)
                users_defined = dup_remove(df_users['name'])
                print(users_defined)
                for i in users_defined:
                    df_total_visits = pd.read_sql("SELECT * FROM users WHERE (name LIKE '{}') ".format(i), conn)
                    total_visits.append(len(df_total_visits['name']))
                conn.close()
                return render_template('admin.html', tripple = zip(users_defined, total_visits), form=form)
            else:
                error_login = "Feil passord"
                return render_template('admin_login.html', form = form, error_login = error_login)
    return render_template('admin_login.html', form = form)




# @app.route('/sys/admin', methods=['GET', 'POST'])
# def admin():
#     try:
#         total_visits = []
#         conn = sql.connect("real.db")
#         df_users = pd.read_sql("SELECT * FROM users ", conn)
#         users_defined = dup_remove(df_users['name'])
#         print(users_defined)
#         for i in users_defined:
#             df_total_visits = pd.read_sql("SELECT * FROM users WHERE (name LIKE '{}') ".format(i), conn)
#             total_visits.append(len(df_total_visits['name']))
#         conn.close()
#         return render_template('admin.html', tripple = zip(users_defined, total_visits), form=form)
#     except:
#         return "Error!"



# thread = threading.Thread(target=foo)
# thread.start()




 
if __name__ == "__main__":

    app.run()


