from flask import Flask, render_template, flash, session, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField 
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Shell, Manager
from flask,ext.mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
manager = Manager(app)

# mail
app.config['MAIL_SERVER'] = 'smtp.googlemail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)


# form
class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()]) 
    submit = SubmitField('Submit')


# database
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        # store the name in session
        session['name'] = form.name.data
        return redirect(url_for('index'))

    return render_template('index.html',
        form = form, 
        name = session.get('name'),
        known = session.get('known', False))

@app.errorhandler(404) 
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    app.run(debug = True)

























