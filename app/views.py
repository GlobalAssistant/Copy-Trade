from flask import Flask, render_template, request, redirect
from threading import Thread
import csv
import logging
from binance.client import Client
from engine import run
from start import app
# # from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# import os

# basedir = os.path.abspath(os.path.dirname(__file__))

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'super secret key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
# db = SQLAlchemy(app)

# app.config.from_object(__name__)

@app.route("/run", methods=['GET'])
def run_process():
    run()
    # print("no run")
    return redirect("/", code=302)


@app.route('/master', methods=['POST'])
def master_form():
    print(request.form['comment_content'])
    print(request.form['comment_content2'])
    print(request.form['comment_content3'])
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO keys (name,key,secret,type) VALUES (?,?,?,?)", (
            request.form['comment_content3'], request.form['comment_content'], request.form['comment_content2'],
            "master"))
        con.commit()
        print("Record successfully added")

    con.close()

    return redirect("/", code=302)

@app.route("/stop", methods=['GET'])
def set_stop_run():
    logger = logging.getLogger('cct')
    global stop_run
    if not stop_run:
        logger.warning('You cannot stop without starting. Think about it :)')
        return redirect("/")
    stop_run = False
    set_stop_run.container.stop()
    logger.info('WebSocket closed')
    return redirect("/", code=302)

@app.route('/delete_master')
def delete_master():
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("delete from keys where type='master'")
        con.commit()
        print("Record successfully deleted")
    con.close()
    return redirect("/", code=302)


@app.route('/delete_slave')
def delete_slave():
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("delete from keys where type='slave'")
        con.commit()
        print("Record successfully deleted")
    con.close()
    return redirect("/", code=302)


@app.route('/slave', methods=['POST'])
def slave_form():
    print(request.form['comment_content'])
    print(request.form['comment_content2'])
    print(request.form['comment_content3'])
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO keys (name,key,secret,type) VALUES (?,?,?,?)", (
            request.form['comment_content3'], request.form['comment_content'], request.form['comment_content2'],
            "slave"))
        con.commit()
        print("Record successfully added")
    con.close()
    return redirect("/", code=302)


@app.route('/')
def homepage():

    return render_template("home.html")


# if __name__ == "__main__":
#     app.run(host='127.0.0.1', debug=True)
