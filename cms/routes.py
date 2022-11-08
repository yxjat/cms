from cms.model import greviences, user,post,enrolled
from flask import render_template, url_for, flash, redirect, request, abort
from cms.forms import enrollment_form, regform, loginform,updateprof,post_form,conformation_form, request_reset_form,password_reset, contactForm
from cms import app,db,bcrypt,mail
from flask_login import login_user, current_user,logout_user, login_required
import secrets
import os
from PIL import Image
from flask_mail import Message



@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type = int)
    posts = post.query.order_by(post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('home.html', posts = posts)

@app.route('/hello')
def hello():
    return 'Hell, World'

@app.route('/about')
def about():
    return render_template('about.html', title = "About Page")

@app.route('/register', methods= ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = regform()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        us = user(username= form.username.data, email = form.email.data, password = hashed_pw, isProf = form.isProf.data)
        db.session.add(us)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', title = "Register", form =form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = loginform()
    if form.validate_on_submit():
        if user.query.filter_by(email= form.email.data).first():
            us = user.query.filter_by(email= form.email.data).first()
            if bcrypt.check_password_hash(us.password,form.password.data):
                login_user(us,form.remember.data)
                flash(f"Welcome, {us.username}", 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash("Incorrect Password", 'danger')
        elif user.query.filter_by(username = form.email.data).first():
            us = user.query.filter_by(username = form.email.data).first()
            if bcrypt.check_password_hash(us.password,form.password.data):
                login_user(us,form.remember.data)
                flash(f"Welcome, {us.username}", 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash("Incorrect Password", 'danger')
        else:
            flash("Login unsuccessful. Please recheck the details." ,'danger')
    return render_template('login.html', title = "Login", form =form)

@app.route('/logout')
def logout():
    logout_user()
    flash(f"Logout Successful", "danger")
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics/', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods= ['GET', 'POST'])
@login_required
def account():
    form = updateprof()
    
    if form.validate_on_submit():
        #print("yesssss")
        if form.picture.data:
            print("yesssss")
            pic_file = save_picture(form.picture.data)
            current_user.image_file = pic_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.repp.data:
            current_user.image_file = "default.jpeg"
        db.session.commit()
        flash(f'Account updated for {form.username.data}!', 'success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename= 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file,form = form)
    
@app.route('/posts/new', methods= ['GET', 'POST'])
@login_required
def new_post():
    form = post_form()
    if current_user.isProf == True:
        if form.validate_on_submit():
            po = post(title = form.title.data, content= form.content.data, author = current_user, credit = form.credit.data)
            db.session.add(po)
            db.session.commit()
            flash("Your post has been created!", 'success')
            return redirect(url_for('home'))
    
    else:
        flash("Unauthorized" , 'danger')
        return redirect(url_for('home'))
    
    return render_template('create_post.html', title= "New Post", form= form, legend = "New Post")

@app.route('/posts/<int:post_id>', methods= ['GET', 'POST'])
@login_required
def viewpost(post_id):
    po = post.query.get_or_404(post_id)
    form = enrollment_form()
    if form.validate_on_submit():
        en = enrolled(name = form.name.data, course = po.title, teach = po.author.username,member = current_user,credit = po.credit)
        db.session.add(en)
        db.session.commit()
        flash(f'{current_user.username} has been enrolled in {po.title} Successfully' , 'success')
        return redirect(url_for('home'))
    return render_template('post.html', title = po.title, post = po, current_user = current_user, form = form )

@app.route('/users/<string:username>')
@login_required
def viewuser(username):
    us = user.query.filter_by(username = username).first_or_404()
    image_file = url_for('static', filename= 'profile_pics/' + us.image_file)
    page = request.args.get('page', 1, type=int)
    user_posts = post.query.filter_by(author=us).order_by(post.date_posted.desc()).paginate(page=page, per_page=5)
    user_courses = enrolled.query.filter_by(user_id = us.username).all()
    return render_template('user.html', title = us.username, user = us, image_file = image_file, posts = user_posts,courses = user_courses, len = len(user_courses))

@app.route('/posts/<int:post_id>/update', methods= ['GET', 'POST'])
@login_required
def update_post(post_id):
    po = post.query.get(post_id)
    if po.author != current_user:
        abort(403)
    form = post_form()
    if form.validate_on_submit():
        po.title = form.title.data
        po.content = form.content.data
        db.session.commit()
        flash(f'{po.title} has been updated', 'success')
        return redirect(url_for('viewpost', post_id =po.id))
    elif request.method == 'GET':
        form.title.data = po.title
        form.content.data = po.content
    
    return render_template('create_post.html', title= "Update Post", form= form, legend = "Update Post" )

@app.route('/posts/<int:post_id>/delete', methods =['Get','POST'])
@login_required
def delete_post(post_id):
    po = post.query.get_or_404(post_id)
    form = conformation_form()
    if po.author!= current_user:
        abort(403)
        
    if form.validate_on_submit():
        if form.confirm.data:
            db.session.delete(po)
            db.session.commit()
            flash("Your post has been deleted", 'success')
            return redirect(url_for('home'))
        else:
            flash("The post was not deleted", 'danger')
            return redirect(url_for('home'))
    
    return render_template('delete.html', title = "delete post", pos = po, form = form )
    
def send_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset', sender = 'n_o_reply_@outlook.com', recipients = [user.email])
    msg.body = f''' To reset your password visit the following link:
{url_for('reset_password', token = token, _external = True)}
    
If you did not make this request then simply ignore it.
    
'''
    mail.send(msg)


@app.route('/reset_password', methods= ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = request_reset_form()
    if form.validate_on_submit():
        us = user.query.filter_by(email = form.email.data).first()
        send_email(us)
        flash('An email has been send with instructions to reset your password','info')
        
    return render_template('reset_request.html', title = "Reset password", form = form)

@app.route('/reset_password/<token>', methods= ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    us = user.verify_reset_token(token)
    if us is None:
        flash('This is token is invalid or expired', 'warning')
        return redirect(url_for('reset_request'))
    form = password_reset()
    if form.validate_on_submit():
        flash(f'Password changed for {us.username}!', 'success')
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        us.password = hashed_pw
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('reset_password.html', title = "Reset password", form = form)

@app.route('/credit')
@login_required
def credit():
    us = current_user
    courses = enrolled.query.filter_by(user_id = us.username).all()
    totalCredits = 160
    creditsRemaining = 160
    creditCnt = 0
    for course in courses:
        creditCnt+=course.credit
        creditsRemaining-=course.credit
    return render_template('credit.html', title = "Credit Page", credit =  creditCnt, creditsRemaining = creditsRemaining)

@app.route('/contact', methods= ['GET', 'POST'])
def contactUs():
    form = contactForm()
    if form.validate_on_submit():
        flash(f'{form.name.data}, your feedback has been recorded')
        gr = greviences(name = form.name.data, email = form.email.data, content = form.content.data)
        db.sessions.add(gr)
        db.sessions.commit()
    return render_template('contactUs.html', form = form)