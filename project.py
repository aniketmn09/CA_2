from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

with open('config.json','r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'aniket09'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri'] 

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():

    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts = posts)


    if request.method == 'POST':
       username = request.form.get('uname')
       userpass = request.form.get('pass')
       if (username == params['admin_user'] and userpass == params['admin_password']):
           session['user'] = username
           posts = Posts.query.all()
           return render_template('dashboard.html', params=params, posts = posts)

    return render_template('login.html', params=params)


@app.route("/logout")
def logout():
    session.clear()
    return redirect('/dashboard')


@app.route("/donate")
def donate():
    
    return render_template('donate.html', params=params)
    

@app.route("/add_post", methods = ['GET', 'POST'])
def add_post():
    if(request.method=='POST'):
        title = request.form.get('title')
        tagline = request.form.get('tline')
        slug = request.form.get('slug')
        content = request.form.get('content')
        img_file = request.form.get('img_file')
        date = datetime.now()
        entry = Posts(title=title, tagline=tagline, slug=slug, content=content, img_file=img_file, date=date )
        db.session.add(entry)
        db.session.commit()    
    return render_template('add_post.html', params=params)


@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')       


@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit_route(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method =='POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug 
                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/dashboard')                 
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)
            # else:
            #     post = Posts.query.filter_by(sno=sno).first()
            #     post.title = box_title
            #     post.slug = slug
            #     post.content = content
            #     post.tagline = tline
            #     post.img_file = img_file
            #     post.date = date
            #     db.session.commit()
            #     return redirect('/dashboard')
                

        # post = Posts.query.filter_by(sno=sno).first()            
        



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html', params=params)    

if __name__ == '__main__':
    app.run(debug=True)    