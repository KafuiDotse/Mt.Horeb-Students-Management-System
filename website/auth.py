from flask import Blueprint,render_template,request,url_for,redirect,flash
from flask_login import login_user,logout_user,login_required,current_user
from .dbModels import User,Course
from .import db


auth=Blueprint("auth",__name__)

@auth.route("/")
def hero():
    return render_template("hero_page.html")

@auth.route("/sign-up", methods=["GET","POST"])
@login_required
def sign_up():
    if current_user.role=="admin":
        courses=Course.query.all()
        if request.method=="POST":
            firstname=request.form.get("firstname")
            lastname=request.form.get("lastname")
            name=f"{firstname} {lastname}"
            email=request.form.get("email")
            role=request.form.get("role")
            course=request.form.get("course")
            password=request.form.get("password")
            conf_password=request.form.get("confirm_password")

            if len(firstname)==0:
                flash("First Name is empty!",category="error")
            elif len(lastname)==0:
                flash("Last Name is empty!",category="error")
            elif len(email)==0:
                flash("Email is empty!",category="error")
            elif len(password)<=4:
                flash("Password is to short!",category="error")
            elif password!=conf_password:
                flash("Password does not match!",category="error")
            elif role=="admin":
                user=db.session.query(User.role).first()
                if role in user:
                    flash("Admin already exits!",category="error")
            else:
                user=User(name=name,email=email,role=role,course=course,password=password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("Added successfully",category="success")

        return render_template("admin/sign_up.html",user=current_user,courses=courses)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@auth.route("/login", methods=["GET","POST"])
def login():
    admin=User.query.filter_by(role="admin").first()
    if admin:
        pass
    else:
        user=User(name="Kafui Doste",email="kafui@gmail.com",password="123456",role="admin",course="None")
        db.session.add(user)
        db.session.commit()
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        user=User.query.filter_by(email=email).first()
        if user:
            if user.password != password:
                flash("Password is incorrect!",category="error")

            else:
                login_user(user,remember=True)
                flash("You have successfully logged in",category="success")
                if current_user.role=="admin":
                    return redirect(url_for("views.dashboard"))
                elif current_user.role=="teacher":
                    return redirect(url_for("views.semister_level"))
                
        else:
            flash("Email does not exist!",category="error")

    return render_template("admin/login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))