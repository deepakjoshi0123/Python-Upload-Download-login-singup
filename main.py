
from io import BytesIO
import os
from flask import Flask ,render_template,request,redirect,flash, send_file,url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = b'secret'
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

class Item(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,unique=True,nullable=False)
    data = db.Column(db.LargeBinary)

db.create_all()

BASE_PATH = os.getcwd()
ALLOWED_EXTENSION = {'txt','pdf','jpg','jpeg','gif','png'}

def allowed_files(filename: str) -> bool :
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION

@app.route('/',methods=['GET','POST'])
def index():
    print(BASE_PATH)
    if request.method == 'POST':
        print('heyyy there')
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

@app.route('/download/<int:id>',methods=['GET'])
def download():
    item=Item().query.filter_by(id=id).first()
    # print('check item',item)
    return send_file(BytesIO(item.data),mimetype='image/png',as_attachment=True,attachment_filename=item.name)

app.run()