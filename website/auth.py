from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


from flask_mail import Message
import random
from datetime import datetime, timedelta
from flask import session

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'request':
            # Generate and send new OTP
            otp_code = str(random.randint(100000, 999999))
            session['otp_code'] = otp_code
            session['otp_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            msg = Message(subject='Your OTP Code',
                          sender='youremail@gmail.com',
                          recipients=['adrianjennelltiamzon@gmail.com'])
            msg.body = f'Your OTP code is: {otp_code}\n\nIt expires in 5 minutes.'
            mail.send(msg)

            flash("OTP sent to boss email. It will expire in 5 minutes.", category="info")

        elif action == 'submit':
            input_otp = request.form.get('otp')

            stored_otp = session.get('otp_code')
            otp_time = session.get('otp_timestamp')

            if stored_otp and otp_time:
                otp_time = datetime.strptime(otp_time, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()

                if now - otp_time > timedelta(minutes=5):
                    flash("OTP has expired. Please request a new one.", category="error")
                    session.pop('otp_code', None)
                    session.pop('otp_timestamp', None)
                elif input_otp == stored_otp:
                    user = User.query.filter_by(email='adrianjennelltiamzon@gmail.com').first()
                    login_user(user, remember=True)
                    session.permanent = True
                    flash("Logged in successfully with OTP.", category="success")
                    session.pop('otp_code', None)
                    session.pop('otp_timestamp', None)
                    return redirect(url_for('views.home'))
                else:
                    flash("Invalid OTP. Please try again.", category="error")
            else:
                flash("No OTP found. Please request one first.", category="error")

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()

    # Clear OTP session data
    session.pop('otp_code', None)
    session.pop('otp_timestamp', None)

    flash("You have been logged out. Please request a new OTP to log in again.", category="info")
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
