from app import app

from flask import redirect, url_for, render_template, request, session, flash, g, jsonify
from datetime import timedelta

import os
from bs4 import BeautifulSoup, NavigableString
import base64
import uuid
from markupsafe import Markup

import html

from app import db_op

app.secret_key = "sakratka"
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['UPLOAD_FOLDER'] = './app/static/uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_db():
    if 'db' not in g:
        g.db = db_op.Database()  # Create a new Database instance for the request
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()  # Close the connection after the request ends

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form['username']
        password = request.form['password']
        if user == "" or password == "":
            flash("please enter username and password", "status")
            return redirect(url_for("login"))

        session.permanent = True
        verify = get_db().user_verify(user, password)
        if verify == True:
            session["user"] = user
            return redirect(url_for("feed"))
        else:
            flash('Username or Password is Incorrect', 'status')
            return redirect(url_for("login"))
    elif request.method == 'GET':
        if "user" in session:
            return redirect(url_for("feed"))
        else:
            return render_template("login.html")

@app.route('/signup', methods = ["POST","GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("All fields are required", "status")
            return redirect(url_for("signup"))

        # Save user details to the database
        
        result = get_db().user_add(username, password)
        if result == -1:
            flash("Error in Signup", "status")
            return render_template("signup.html")
        
        flash("Account created successfully. Please log in.", "status")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/profile",methods=["GET","POST"])
def profile():
    if "user" in session:
        if request.method == 'GET':
            user_det = get_db().get_profile(session['user'])
            
            return render_template('profile.html',  
                                email=user_det['email'] if 'email' in user_det.keys() and user_det['email'] is not None else 'Not provided', 
                                address=user_det['address'] if 'address' in user_det.keys() and user_det['address'] is not None else 'Not provided', 
                                contact_number=user_det['contact_number'] if 'contact_number' in user_det.keys() and user_det['contact_number'] is not None else 'Not provided'
                                )


        elif request.method == "POST":
            username = session['user']
            email = request.form["email"]
            contact_number = request.form["contact_number"]
            address = request.form["address"]

            # Update user details in the database
            get_db().profile_edit(username, email, contact_number, address)

            # Update session variables
            session["email"] = email
            session["contact_number"] = contact_number
            session["address"] = address

            return render_template(
                'profile.html', 
                username=session['user'], 
                email=session["email"], 
                contact_number=session["contact_number"], 
                address=session['address']
            )

        flash("sucessfully loged in","status")
        return render_template('profile.html',username = session['user'])

    return redirect(url_for('login'))

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        if 'user' not in session:
            return redirect(url_for('login'))
        title = request.json['title']
        content = request.json['content']
        soup = BeautifulSoup(content, 'html.parser')

        # Process and save images
        for img in soup.find_all('img'):
            src = img.get('src')
            if src.startswith('data:image'):
                header, encoded = src.split(',', 1)
                img_data = base64.b64decode(encoded)
                ext = header.split('/')[1].split(';')[0]
                filename = f"{uuid.uuid4().hex}.{ext}"
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                with open(path, 'wb') as f:
                    f.write(img_data)

                img['src'] = url_for('static', filename=f'uploads/{filename}')

        # Save the updated HTML
        body = str(soup)
        session['user_id'] = get_db().get_user_id(session['user'])
        result = get_db().add_post(session['user_id'], title, body)
        
        if result == -1:
            return jsonify({'error': 'An error occurred while creating the post.'}), 500
        else:
            flash('Your post has been successfully published!', 'success')
            return jsonify({'success': 'Post created successfully!'}), 200

    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('create_post.html')
        
@app.route('/')
@app.route('/feed', methods=['GET'])
def feed():
    if  'user' not in session:
        return redirect(url_for('login'))
    user_id = get_db().get_user_id(session['user'])
    raw_posts = get_db().get_recommendations_from_similar_users(user_id,5)
    posts = []

    for row in raw_posts:
        post = dict(row)
        unescaped_body = html.unescape(post['body'])
        soup = BeautifulSoup(unescaped_body, 'html.parser')
        clean_soup = BeautifulSoup('', 'html.parser')

        for elem in soup.descendants:
            if isinstance(elem, NavigableString):
                clean_soup.append(elem)
            elif elem.name == 'img' and elem.has_attr('src'):
                img = clean_soup.new_tag('img', src=elem['src'])
                clean_soup.append(img)
            elif elem.name == 'p':
                # Create clean <p> and add only its text and <img> children
                new_p = clean_soup.new_tag('p')
                for child in elem.descendants:
                    if isinstance(child, NavigableString):
                        new_p.append(child)
                    elif child.name == 'img' and child.has_attr('src'):
                        img = clean_soup.new_tag('img', src=child['src'])
                        new_p.append(img)
                clean_soup.append(new_p)

        post['body'] = str(clean_soup)
        posts.append(post)

    return render_template('feed.html', posts=posts)

@app.route('/like', methods=['POST'])
def like_post():
    if 'user' not in session:
        return jsonify({'redirect': url_for('login')}), 401  # custom redirect flag

    user_id = get_db().get_user_id(session['user'])
    post_id = request.json.get('post_id')
    result = get_db().like_post(user_id, post_id)

    if result == -1:
        return jsonify({'error': 'An error occurred while liking the post.'}), 500
    else:
        return jsonify({'success': 'Post liked successfully!'}), 200

@app.route('/dislike', methods=['POST'])
def dislike_post():
    if 'user' not in session:
        return jsonify({'redirect': url_for('login')}), 401

    user_id = get_db().get_user_id(session['user'])
    post_id = request.json.get('post_id')
    result = get_db().dislike_post(user_id, post_id)

    if result == -1:
        return jsonify({'error': 'An error occurred while disliking the post.'}), 500
    else:
        return jsonify({'success': 'Post disliked successfully!'}), 200

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("you are loged out", "status")
    return redirect(url_for('login'))