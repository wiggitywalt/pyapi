from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os


app = Flask(__name__)
#db stuff starts here
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'wlk01.db')
db = SQLAlchemy(app)

#db init stuff
@app.cli.command('dbcreate')
def db_create():
    db.create_all()
    print("db create all has run.")

@app.cli.command('dbdrop')
def db_drop():
    db.drop_all()
    print("db drop all has run.")

@app.cli.command('dbseed')
def db_seed():
    dostuff01 = Task(name="do this stuff", type="email")
    walter = User(first_name="Walter", last_name="Kimbrough", email="walt.kimbrough@me.com", password="jorples!")
    amy = User(first_name="Amy", last_name="Kimbrough", email="Amy@aol.com", password="whattawhat?")
    db.session.add(dostuff01)
    db.session.add(walter)
    db.session.add(amy)
    db.session.commit()
#end, db stuff

@app.route('/')
def hello_world():
    return 'hello worldy world'

@app.route('/about')
def about():
    return jsonify(jasm='about a boy')

@app.route('/whoyou')
def whoyou():
    name = request.args.get('name')
    return jsonify(message='howdy, ' + name), 200

@app.route('/cleanwhoyou/<string:name>/<int:age>')
def cleanwhoyou(name: str,age: int):
    return jsonify(message='you are ' + str(age) + ' years old, ' + name)

@app.route('/notfound')
def notFound():
    return jsonify(message='not found, bitch'), 404

#begin, models (move to sep file later)
#######################################
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Task(db.Model):
    __tablename__= 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
#######################################
#end, models

if __name__ == '__main__':
    print('starting...')
    app.run()
