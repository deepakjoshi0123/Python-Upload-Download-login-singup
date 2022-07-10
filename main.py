
from io import BytesIO
import os
from flask import Flask ,render_template,request,redirect,flash, send_file,url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = b'secret'
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

class Item(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,unique=True,nullable=False)
    data = db.Column(db.LargeBinary)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String,unique=True,nullable=False)
    


BASE_PATH = os.getcwd()
ALLOWED_EXTENSION = {'txt','pdf','jpg','jpeg','gif','png'}

def allowed_files(filename: str) -> bool :
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION

# @app.route('/login',methods=['POST'])
# def login():
#     if request.method=='POST':
#         username=request.form.get('name')
#         password=request.form.get('password')
#         usernamedata=db.execute('SELECT username FROM User WHERE username=:username',{'username':username}).fetchone()
#         passworddata=db.execute('SELECT password FROM User WHERE username=:username',{'username':username}).fetchone()

#         if usernamedata is None:
#             flash('No username','danger')
#             return render_template('login.html')
#         else:
#             for passwor_data in passworddata:
#                 if sha256_crypt.verify(password,passwor_data):
#                     session=True
#                     flash('You are now logged in!!')
#                     return redirect(url_for('/')) 
#                 else:
#                     flash('incorrect password')
#                     return render_template('login.html')


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        confirm=request.form.get('confirm')
        secure_password=sha256_crypt.encrypt(str(password))
        print(email,'check it ------->')
        usernamedata = User().query.filter_by(email=email).first()
        
        print('------>',usernamedata,password,confirm)
        # usernamedata=db.execute('SELECT username FROM User WHERE email=:email',{'email':email}).fetchone()
        if usernamedata==None:
            if password==confirm:
                usr = User(email=email,password=secure_password)
                db.session.add(usr)
                db.session.commit()
                print(password==confirm,"heyyyyyyyyyyyyyyyyyy")
                flash('You are registered and can now login')
                return redirect(url_for('login'))
            else:
                flash('password does not match')
                return render_template('register.html')
        else:
            flash('user already existed, please login or contact admin')
            return redirect(url_for('login'))
    return render_template('signup.html')
@app.route('/',methods=['GET','POST'])
def index():
    print(BASE_PATH)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files.get('file')
        
        if file.filename == '':
            flash('No file was selected')
            return redirect(request.url)
        if file and allowed_files(file.filename):
            # filename = secure_filename(file.filename)
            # file.save(os.path.join(BASE_PATH,'',filename))
            new_file = Item(name=file.filename,data=file.read())
            db.session.add(new_file)
            db.session.commit()
            flash('File uploaded successfully')
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/files',methods =['GET'])
def files():
    items = Item().query.all()
    # print(items[0].name)
    return render_template('files.html' , items = items)

@app.route('/download',methods=['GET'])
def download():
    id = request.args.get('id')
    item=Item().query.filter_by(id=id).first()
    print('check item',item)
    return send_file(BytesIO(item.data),mimetype='image/png',as_attachment=True,attachment_filename=item.name)
    
db.create_all()
app.run()