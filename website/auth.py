from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User, OTPCode2
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import and_


auth = Blueprint('auth', __name__)


from flask_mail import Message
import random
from datetime import datetime, timedelta
from flask import session

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')

        now = datetime.utcnow()
        expiry_time = now - timedelta(minutes=5)  # Define early so it's always available

        if action == 'request':
            otp_code = str(random.randint(100000, 999999))
            timestamp = now

            new_otp = OTPCode2(code=otp_code, created_at=timestamp)
            db.session.add(new_otp)
            db.session.commit()

            msg = Message(subject='Your OTP Code',
                          sender='youremail@gmail.com',
                          recipients=['adrianjennelltiamzon@gmail.com'])
            msg.body = f'Your OTP code is: {otp_code}\n\nIt expires in 5 minutes.'
            mail.send(msg)

            flash("OTP sent to boss email. It will expire in 5 minutes.", category="info")

        elif action == 'submit':
            input_otp = request.form.get('otp')

            # Find a valid OTP
            otp_entry = OTPCode2.query.filter_by(code=input_otp).filter(OTPCode2.created_at >= expiry_time).first()

            if otp_entry:
                # Log in the boss user
                user = User.query.filter_by(email='adrianjennelltiamzon@gmail.com').first()
                if user:
                    login_user(user, remember=True)
                    flash("Logged in successfully with OTP.", category="success")

                    # Remove used OTP
                    db.session.delete(otp_entry)
                    db.session.commit()

                    return redirect(url_for('views.home'))
                else:
                    flash("User not found.", category="error")
            else:
                flash("Invalid or expired OTP. Please try again.", category="error")

        # Cleanup: Remove expired OTPs from the database
        OTPCode2.query.filter(OTPCode2.created_at < expiry_time).delete()
        db.session.commit()

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="info")
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
