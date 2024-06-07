from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from .auth import role_required

admin= Blueprint('admin', __name__)


@admin.route('/dashboard', methods=['GET', 'POST'])
@role_required('Admin')
@login_required
def dashboard():
    return render_template("Admin/dashboard.html", user=current_user)