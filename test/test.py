# pip install Flask
# pip install flask_sqlalchemy
# flask --app test run

# https://www.tiny.cloud/blog/self-host-tinymce/
# sed -i 's@Upgrade@Z@g' themes/silver/theme.min.js
# sed -i 's@https://www.tiny.cloud/tinymce-self-hosted-premium-features/?utm_source=TinyMCE&utm_medium=SPAP&utm_campaign=SPAP&utm_id=editorreferral@x@g' themes/silver/theme.min.js
# sed -i 's@https://www.tiny.cloud/powered-by-tiny?utm_campaign=editor_referral&utm_medium=poweredby&utm_source=tinymce&utm_content=v6@x@g' themes/silver/theme.min.js

import os
from flask import Flask
from flask import url_for, render_template, request, redirect, send_from_directory, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
db = SQLAlchemy(app)
from models import *

@app.route("/")
def hello_world():
  return "<p>Hello, World!</p>"
    
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    return do_the_login()
  else:
    return show_the_login_form()
    
class Post:
  def __init__(self):
    self.id    = 0
    self.title = "xxx"
    self.link  = "yyy"
    self.date = "date"
    self.data = "data"
    self.hashtags = ["x", "y", "z"]
    self.photos = ["ph1", "ph2", "ph3", "ph4"]
    
class Blog:
  def __init__(self):
    self.groups = ["ходитъ", "думатъ", "готовитъца", "затаилъсо"]
        
@app.route("/post")
def post():
  post = Post()
  post.next = Post()
  post.prev = Post()
  return render_template('post.html', post=post, blog=Blog() )
  
@app.route("/edit")
def edit():
  post = Post()
  post.next = Post()
  post.prev = Post()
  return render_template('admin.html', post=post, blog=Blog() )
  
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  
@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    
@app.route('/postData', methods=['POST'])
def postData():

  print( request.json )
  
  return jsonify( { "status" : "ok" } )
  
@app.route('/postImage', methods=['GET', 'POST'])
def postImage():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify( { "location" : url_for('download_file', name=filename) } )
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>SQLALCHEMY_DATABASE_URI
    '''
        
with app.test_request_context():
  print( url_for('static', filename='index.html') )
  print( url_for('static', filename='index.html') )
  print( url_for('static', filename='style.css') )      
  
if __name__ == '__main__':
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.config['UPLOAD_FOLDER'] = "uploads"
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SQLALCHEMY_DATABASE_URI'] = 
  
  app.run(debug=True, host='0.0.0.0')
  
  
