# pip install Flask
# pip install flask_sqlalchemy
# flask --app test run

# https://www.tiny.cloud/blog/self-host-tinymce/
# sed -i 's@Upgrade@Z@g' themes/silver/theme.min.js
# sed -i 's@https://www.tiny.cloud/tinymce-self-hosted-premium-features/?utm_source=TinyMCE&utm_medium=SPAP&utm_campaign=SPAP&utm_id=editorreferral@x@g' themes/silver/theme.min.js
# sed -i 's@https://www.tiny.cloud/powered-by-tiny?utm_campaign=editor_referral&utm_medium=poweredby&utm_source=tinymce&utm_content=v6@x@g' themes/silver/theme.min.js

import os, time
from datetime import date
from flask import Flask, flash
from flask import url_for, render_template, request, redirect, send_from_directory, jsonify, json
from flask_login import login_user, login_required, logout_user, LoginManager, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
BLOG_TESTBED = True

DB_PASS     = "test123"
DB_RECREATE = True
POST_STATUS_OPEN = "виден"

app.config['SECRET_KEY'] = 'secret-key-goes-here' #FIXME
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:" + DB_PASS + "@localhost:5432/blog"

# LOGIN MANAGER
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  answer = UserMixin()
  answer.id = int(user_id)
  return answer

# DB
db = SQLAlchemy(app)
class UserDB(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())
  key  = db.Column(db.String())
  
hashtagPostConnections = db.Table(
    "hashtags_posts_connections",
    db.Column("postId", db.ForeignKey("posts.id")),
    db.Column("hashtagId", db.ForeignKey("hashtags.id")),
)

class PostDB(db.Model):
  __tablename__ = 'posts'

  id = db.Column(db.Integer, primary_key=True)
  postStatus = db.Column(db.String())
  postGroup  = db.Column(db.String())
  postStart  = db.Column(db.String())
  postEnd    = db.Column(db.String())
  title = db.Column(db.String())
  dateCreated = db.Column(db.Date())
  dateUpdated = db.Column(db.Date())
  data = db.Column(db.LargeBinary())
  
  hashtags = db.relationship('HashtagDB', secondary=hashtagPostConnections, backref='posts')
  
class HashtagDB(db.Model):
  __tablename__ = 'hashtags'
  id = db.Column(db.Integer, primary_key=True)
  hashtag = db.Column(db.String())

class Blog:
  def __init__(self):
    self.groups  = ["ходитъ", "думатъ", "готовитъца", "затаилъсо"]
    self.statuss = ["виден", "скрыт"]
    self.has_user = current_user.is_authenticated
  
class Post():
  def __init__(self):
    self.id = 0
    self.postStatus = ""
    self.postGroup = ""
    self.postStart = ""
    self.postEnd = ""
    self.title = ""
    self.dateCreated = ""
    self.dateUpdated = ""
    self.data = ""
    self.hashtags = []
    
class Hashtag:
  def __init__(self):
    self.name = ""
    self.link = ""
    
@app.route("/")
def routeDef():
  return redirect(url_for('routePost'), 301)

@app.route("/ctl/reset")
def routeReset():
  if BLOG_TESTBED:
    if DB_RECREATE:
        db.drop_all()
        db.create_all()
  return "<p>Hello, World!</p>"
  
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    # login code goes here
    user = request.json['user']
    password = request.json['pass']
    remember = True
    
    print( "Auth:", user, password )

    # FIXME
    SITE_USER = "user"
    SITE_PASSWORD=generate_password_hash("password", method='scrypt')
    print( SITE_PASSWORD )
    
    if user != SITE_USER and not check_password_hash(password, SITE_PASSWORD):
        print("incorrect user!")
        time.sleep(5)
        return 'ошибочка'

    # if the above check passes, then we know the user has the right credentials
    user = load_user(0)
    login_user(user, remember=remember)
    print("user ok!")
    return 'приветик'
  else:
    return render_template('login.html', blog=Blog() )
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
    
def get_post_link( id ):
  return "/post?id=" + str( id )
    
def init_post(post, postDB):
  post.id = postDB.id
  post.postStatus = postDB.postStatus
  post.postGroup  = postDB.postGroup
  post.postStart  = postDB.postStart
  post.postEnd    = postDB.postEnd
  post.title      = postDB.title
  post.dateCreated = postDB.dateCreated
  post.dateUpdated = postDB.dateUpdated
  post.data = postDB.data.decode('utf8')
  post.link = get_post_link( post.id )
  for tag in postDB.hashtags:
    h = Hashtag()
    h.name = tag.hashtag
    h.link = "/list?tag=" + h.name
    post.hashtags += [ h ]
    
def init_post_list(postDBs):
  answer = []
  for pDB in postDBs:
    post = Post()
    init_post(post, pDB)
    post.data = ""
    print( post.postStatus, post.postGroup, post.postStart, post.postEnd, post.title )
    answer += [ post ]
  return answer
  
def make_post_list(postDBs):
  answer = []
  for postDB in postDBs:
    post = Post()
    init_post(post, postDB)
    post.data = None
  return answer
  
def init_empty_post():
  post = Post()
  post.link = ""
  post.title = "ничего"
  return post
  
@app.route("/list")
def routeList():
  args = {}
  try:
    args = request.args.to_dict()
  except Exception as e: 
    print(e)
    print("args = request.args.to_dict()")
  
  posts = None
  postFilter = None
  filtersRaw = ""
  if "secret" in args:
    posts = db.session.query(PostDB).filter(PostDB.postStatus != POST_STATUS_OPEN).order_by(PostDB.id.desc()).all()
    postFilter = "по сокрытому"
    filtersRaw = "secret=secret"
  elif "group" in args:
    group = args[ "group" ]
    posts = db.session.query(PostDB).filter(PostDB.postGroup == group).filter(PostDB.postStatus == POST_STATUS_OPEN).order_by(PostDB.id.desc()).all()
    postFilter = "по листу " + group
    filtersRaw = "group=" + group
  elif "tag" in args:
    tag = str(args[ "tag" ])
    hashtag = db.session.query(HashtagDB).filter(HashtagDB.hashtag == tag).first()
    if hashtag : 
      posts = hashtag.posts
      posts = [ post for post in posts if post.postStatus == POST_STATUS_OPEN ]
      posts = sorted( posts, key=lambda x: x.id, reverse=True )
    postFilter = "по метке " + tag
    filtersRaw = "tag=" + tag
  else :
    posts = db.session.query(PostDB).filter(PostDB.postStatus == POST_STATUS_OPEN).order_by(PostDB.id.desc()).all()
    postFilter = "всё"
    filtersRaw = ""
  
  try:
    postsPerPage = 25
    maxPagesToList = 11
    nPosts = len(posts)
    nPages = nPosts // postsPerPage
    # if nPosts == nPages * postsPerPage : nPages += 1
    offset = 0
    page   = 0
    if "page" in args:
      page = int(args[ "page" ])
      page = max(0, page)
      page = min(page, nPosts)
      offset = int(page)*postsPerPage
    postStart = min(nPosts, offset)
    postEnd   = min(nPosts, offset + postsPerPage)
    posts = posts[ postStart : postEnd ]
    blogPosts = init_post_list( posts )
    pages = list( range( max(0, page - maxPagesToList), min(nPages+1, page + maxPagesToList ) ) )
    other = { "nPages" : nPages, "nPosts" : nPosts, "postFilter" : postFilter, "page" : page, "pageNext" : min(page+1, nPages), "pagePrev" : max(page-1, 0), "filtersRaw" : filtersRaw, "pages" : pages }
  except Exception as e: 
    print(e)
    print("list error")
    other = { "nPages" : 0, "nPosts" : 0, "postFilter" : postFilter, "page" : 0, "pageNext" : 0, "pagePrev" : 0, "filtersRaw" : filtersRaw, "pages" : [0] }
    return render_template('postList.html', posts=[], blog=Blog(), other=other )
    
  return render_template('postList.html', posts=blogPosts, blog=Blog(), other=other )
        
@app.route("/post")
def routePost():
  args = request.args.to_dict()
  
  post = Post()
  post.next = init_empty_post()
  post.prev = init_empty_post()

  postDB = None
  
  # we have post ID to get from DB
  if "id" in args:
    id = args[ "id" ]
    if id.isdigit():
      postDB = db.session.query(PostDB).filter(PostDB.id == id).first()
      if postDB.postStatus != POST_STATUS_OPEN:
        if not current_user.is_authenticated:
          postDB = None
      if postDB :
        try:
          init_post(post, postDB)
          postNextDB = db.session.query(PostDB).order_by(PostDB.id).filter(PostDB.id > id).filter(PostDB.postStatus == POST_STATUS_OPEN).first()
          postPrevDB = db.session.query(PostDB).order_by(PostDB.id.desc()).filter(PostDB.id < id).filter(PostDB.postStatus == POST_STATUS_OPEN).first()
          if postNextDB : init_post(post.next, postNextDB)
          if postPrevDB : init_post(post.prev, postPrevDB)
        except Exception as e: 
          print(e)
          print("postDB req error")
          postDB = None
  
  # no post ID - get latest post
  if not postDB:
    postsDB = []
    postsDBs = db.session.query(PostDB).filter(PostDB.postStatus == POST_STATUS_OPEN).order_by(PostDB.id.desc()).limit(5).all()
    if postsDBs:
      postDB = postsDBs[0]
      try:
        init_post(post, postDB)
        if len( postsDBs ) > 1:
          postPrevDB = postsDBs[1]
          if postPrevDB : init_post(post.prev, postPrevDB)
      except Exception as e: 
        print(e)
        print("last postDB req error, return empty post")
        post = Post()
        post.next = init_empty_post()
        post.prev = init_empty_post()
        
  return render_template('post.html', post=post, blog=Blog() )
  
@app.route("/edit")
@login_required
def routeEdit():
  post = Post()
  post.next = Post()
  post.prev = Post()
  post.id = "NEW"
  
  try:
    args = request.args.to_dict()
    if "id" in args:
      id = args[ "id" ]
      if id.isdigit():
        postDB = db.session.query(PostDB).filter(PostDB.id == id).first()
        if postDB :
          init_post(post, postDB)
  except Exception as e: 
    print(e)
    print("routeEdit() edit old post error, return empty post")
    post = Post()
    post.next = Post()
    post.prev = Post()
    post.id = "NEW"
  
  return render_template('admin.html', post=post, blog=Blog() )
  
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
  try:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  except Exception as e: 
    print(e)
    return False
  
@app.route('/uploads/Post()<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    
@app.route('/postData', methods=['POST'])
@login_required
def routePostData():
  print( request.json )
  
  blog = Blog()
  def check_post_request(request):
    try:
      if request.json['postStatus'] not in blog.statuss : return "wrong status"
      if request.json['postGroup']  not in blog.groups : return "wrong group"
      if len( request.json['title'] ) <= 1 : return "wrong title"
      if len( request.json['mytextarea'] ) <= 1 : return "wrong text"
      if 'postId' not in request.json : return "wrong id"
      return None
    except Exception as e: 
      print(e)
      return "something wrong"
  
  statusErr = check_post_request( request )
  if statusErr : return jsonify( { "status" : "not ok", "error" : statusErr } )
  
  postId = request.json['postId']
  if postId == "NEW":
    newPost = PostDB();
    newPost.postStatus = request.json['postStatus']
    newPost.postGroup  = request.json['postGroup']
    newPost.postStart  = request.json['postStart']
    newPost.postEnd    = request.json['postEnd']
    newPost.title = request.json['title']
    newPost.dateCreated = date.today()
    newPost.dateUpdated = None
    newPost.data = request.json['mytextarea'].encode('utf8')
    
    hashtags = request.json['hashtags']
    for hashtag in hashtags :
      tag = db.session.query(HashtagDB).filter(HashtagDB.hashtag == hashtag).first()
      if not tag :
        tag = HashtagDB()
        tag.hashtag = hashtag
        db.session.add(tag)
        
      newPost.hashtags.append(tag)
    
    try:
      db.session.add(newPost)
    except:
      db.session.rollback()
      return jsonify( { "status" : "not ok", "error" : "db error" } )
    else:
      db.session.commit()
      
    return jsonify( { "status" : "ok", "id" : newPost.id, "link" : get_post_link(newPost.id) } )
    
  postId = int( request.json['postId'] )
  oldPost = db.session.query(PostDB).filter(PostDB.id == postId).first()
  if not oldPost:
    return jsonify( { "status" : "no such post" } )
  
  try:
    oldPost.postStatus = request.json['postStatus']
    oldPost.postGroup  = request.json['postGroup']
    oldPost.postStart  = request.json['postStart']
    oldPost.postEnd    = request.json['postEnd']
    oldPost.title = request.json['title']
    oldPost.dateUpdated = date.today()
    oldPost.data = request.json['mytextarea'].encode('utf8')
    
    oldPost.hashtags = []
    hashtags = request.json['hashtags']
    for hashtag in hashtags :
      tag = db.session.query(HashtagDB).filter(HashtagDB.hashtag == hashtag).first()
      if not tag :
        tag = HashtagDB()
        tag.hashtag = hashtag
        db.session.add(tag)
          
      oldPost.hashtags.append(tag)
  except:
    db.session.rollback()
    return jsonify( { "status" : "not ok", "error" : "db error" } )
  else:
    db.session.commit()
    
  return jsonify( { "status" : "ok" } )
  
@app.route('/postImage', methods=['GET', 'POST'])
@login_required
def routePostImage():
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
    </form>
    '''

app.run(debug=BLOG_TESTBED, host='0.0.0.0')
  
  
  
  
  
  
  
  
  
  
