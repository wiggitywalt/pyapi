from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from functools import wraps
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message

app = Flask(__name__)
#db stuff starts here
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'wlk01.db')
app.config['JWT_SECRET_KEY'] = 'superduperdoublethrowdown' #change this to something actually secure, genius
#mailtrap.io config settings
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'c191bb4dbffad3'
app.config['MAIL_PASSWORD'] = '814323a41da293'
#app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
#app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)

##############
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
##############
#############
##-helpers-##
#############
#def login_required(test):
#    @wraps(test)
#    def wrap(*args, **kwargs):
#      if 'logged_in' in session:
#        return test(*args, **kwargs)
#      else:
#        flash('You need to login first, nimrod.')
#        return redirect(url_for('users.login'))
#    return wrap
#############
##-routes--##
#############
@app.route('/')
def hello_world():
    return 'hello worldy world'

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email'];
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='Already registered.'),409
    else:
        #register here.
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name,last_name=last_name,email=email,password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created.'),201


@app.route('/about')
def about():
    return jsonify(jasm='about a boy')

@app.route('/cleanwhoyou/<string:name>/<int:age>')
def cleanwhoyou(name: str,age: int):
    return jsonify(message='you are ' + str(age) + ' years old, ' + name)

@app.route('/notfound')
def notFound():
    return jsonify(message='not found, bitch'), 404

@app.route('/users', methods=['GET'])
def users():
    users_list = User.query.all()
    result = users_schema.dump(users_list)
    return jsonify(result)

@app.route('/tasks', methods=['GET'])
def tasks():
    tasks_list = Task.query.all()
    result = tasks_schema.dump(tasks_list)
    return jsonify(result)    

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email,password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login good', access_token=access_token)
    else:
        return jsonify(message='No login'),401

@app.route('/getemail/<string:email>',methods=['GET'])
def get_it(email:str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message(subject="here ya go!", body="it is " + user.password,sender="admindude@walterspage.com",recipients=["walter.kimbrough@gmail.com"])
        mail.send(msg)
        return jsonify(message="It is on the way. Check ya email.")        
    else:
        return jsonify(message="Unable to complete email message. 991")

@app.route('/note_details/<int:id>', methods=['GET'])
@jwt_required
def note_details(id:int):

    note = Note.query.filter_by(id=id).first()
    if note:
        result = note_schema.dump(note)
        return jsonify(result)
    else:
        return jsonify(message="That note ain't there."),404

@app.route('/update_note', methods=['PUT'])
def updatenote():
    noteid = int(request.form['noteid'])
    note = Note.query.filter_by(id=noteid)
    if note:
         note.summary = request.form['summary']
         note.description = request.form['description']
         db.session.commit()
         return jsonify(msg="Note updated successfully."),202
    else:
        return jsonify(msg="Note not found"),404

#######################################
#begin models (move to sep file later)#
#######################################
class Note(db.Model):
    __tablename__ = 'notes2'
    id = Column(Integer, primary_key=True)
    summary = Column(String)
    description = Column(String)
    userid = Column(Integer)

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

#Marshmallow classes
#add fields here to be deserialized

class NoteSchema(ma.Schema):
    class Meta:
        fields = ('id', 'summary', 'description','userid')

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email')

class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name','type')

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
#######################################
##end models ##########################
#######################################

if __name__ == '__main__':
    print('starting...')
    app.run()
