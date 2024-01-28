from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_csp.csp import csp_header

from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
from . import db
import secrets
auth = Blueprint("auth", __name__)
salt = str(secrets.token_urlsafe(10))
pepper = "M"
from flask import abort
from io import BytesIO
import pyqrcode
from flask import session

@auth.route("/login", methods=['GET', 'POST'])
@csp_header({'default-src':"'none'",'script-src':"'self'"})
def login():

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        otp_verification = request.form.get("remember")

        #TODO sprawdznie wpisywanych danych
        if '"' in username or '"' in password:
            return "Error, pls don't try to hack our page :)"
        user = User.query.filter_by(username=username).first()

        if user:
            if otp_verification == "on" :
                if user.otp:
                    return redirect(url_for('auth.login'))
                    print("Nie logujesz się pierwszy raz")
                if check_password_hash(user.password, f'{user.salt}{password}{pepper}'):
                    login_user(user, remember=True)
                    return redirect(url_for('auth.two_factor_setup'))
                    #return redirect(url_for('views.home'))
                else:
                    print("zle haslo")
                    flash('Password is incorrect.', category='error')
            else:
                otp = request.form.get("otp")
                if otp is not None:
                    otp = int(otp)

                if  check_password_hash(user.password, f'{user.salt}{password}{pepper}') and  user.verify_totp(otp):
                    login_user(user, remember=True)
                    if user.role == "D":
                        return redirect(url_for('views.doctor'))
                    elif user.role == "P":
                        return redirect(url_for('views.patient'))
                else:
                    print('Incorrect password or token.')

        else:
            flash('Username does not exist.', category='error')
            print('nie ma tego username')

    return render_template("index.html", user=current_user)



@auth.route("/logout")
@csp_header({'default-src':"'none'",'script-src':"'self'"})
def logout():
    logout_user()
    return redirect(url_for("views.home"))

@auth.route('/twofactor')
@csp_header({'default-src':"'none'",'script-src':"'self'"})
@login_required
def two_factor_setup():
    # since this page contains the sensitive qrcode, make sure the browser does not cache it
    return render_template('two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@auth.route('/qr')
@csp_header({'default-src':"'none'",'script-src':"'self'"})
@login_required
def qr():

    user = current_user
    print(user)
    # render qrcode for FreeTOTP
    url = qrcode.make(user.get_totp_uri())
    qrcode.make(user.get_totp_uri()).save("website/code.jpg")
    # stream = BytesIO()
    # url.svg(stream, scale=5)
    #return stream.getvalue(), 200
    return jsonify({"sukces"}), 200


@auth.route('/qr_code')
@csp_header({'default-src':"'none'",'script-src':"'self'"})
def qr_code():

    user = current_user
    url = pyqrcode.create(user.get_totp_uri())
    stream = BytesIO()
    url.svg(stream, scale=5)
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}

@auth.route("/check" ,methods=['GET', 'POST'])
@csp_header({'default-src':"'none'",'script-src':"'self'"})
def check_otp():
    if request.method == 'POST':
        otp = request.form.get("otp")


