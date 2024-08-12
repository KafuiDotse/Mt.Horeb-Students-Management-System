from flask import Blueprint,render_template,request,redirect,flash,url_for,session,send_file
from flask_login import login_required,current_user
from . import db
from .dbModels import Students,Course,User,Marks
from .dicts import grade_range
from .pdf import pdf,PDFWithTable,info
import os
import tempfile

views=Blueprint("views",__name__)


@views.route("/dashboard",methods=["POST","GET"])
@login_required
def dashboard():
    if current_user.role=="admin":
        students=Students.query.all()
        session['url']=request.url
        return render_template("admin/dashboard.html",user=current_user,students=students)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))
    
@views.route("/search",methods=["POST","GET"])
@login_required
def search():
    if current_user.role=="admin":
        search=request.form.get('search')
        aspect=request.form.get('aspect')
        std_li=[]

        if aspect=="all":
            std_li=Students.query.all()
        elif aspect=="firstname":
            students=Students.query.filter_by(firstname=search).all()
            std_li=students
        elif aspect=="lastname":
            students=Students.query.filter_by(lastname=search).all()
            std_li=students
        elif aspect=="std_id":
            students=Students.query.filter_by(std_id=search).all()
            std_li=students
        elif aspect=="current_track":
            if search.lower() in "certificate_track":
                students=Students.query.filter_by(current_track="certificate_track").all()
                std_li=students
            elif search.lower() in "diploma_track":
                students=Students.query.filter_by(current_track="diploma_track").all()
                std_li=students
        return render_template("admin/search.html",user=current_user,students=std_li)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))
    

@views.route("/student-info",methods=["GET","POST"])
@login_required
def student_info():
    if current_user.role=="admin":
        if request.method=="POST":
            std_id=request.form.get("std-id")
            firstname=request.form.get("firstname")
            lastname=request.form.get("lastname")
            dob=request.form.get("dob")
            gender=request.form.get("gender")
            pob=request.form.get("pob")
            nationality=request.form.get("nationality")
            admission_date=request.form.get("admission-date")
            current_track=request.form.get("track")

            if len(std_id)==0:
                flash("Student ID is empty",category="error")
            elif len(firstname)==0:
                flash("First Name is empty",category="error")
            elif len(lastname)==0:
                flash("Last Name is empty",category="error")
            elif len(dob)==0:
                flash("Date of Birth is empty",category="error")
            elif len(pob)==0:
                flash("Place of Birth is empty",category="error")
            elif len(nationality)==0:
                flash("Nationality is empty",category="error")
            elif len(admission_date)==0:
                flash("Admission Date  is empty",category="error")

            else:
                student=Students(std_id=std_id,
                                firstname=firstname,
                                lastname=lastname,
                                dob=dob,
                                gender=gender,
                                pob=pob,
                                nationality=nationality,
                                admisision_date=admission_date,
                                current_track=current_track
                                )
                db.session.add(student)
                db.session.commit()
                courses=Course.query.all()
                for course in courses:
                    student.offers.append(course)
                    db.session.commit()
                    
        return render_template("admin/student_info.html",user=current_user)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/add-course",methods=["POST","GET"])
@login_required
def add_course():
    if current_user.role=="admin":
        if request.method=="POST":
            course_name=request.form.get("course_name")
            credit=request.form.get("credit")
            course=Course(name=course_name,credit=credit)
            db.session.add(course)
            db.session.commit()
            flash("Courses Added",category="success")
        return render_template("admin/add_course.html",user=current_user)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/view-course",methods=["POST","GET"])
@login_required
def view_course():
    if current_user.role=="admin":
        courses=Course.query.all()
        return render_template("admin/view_course.html",user=current_user,courses=courses)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/update-course/<int:id>",methods=["POST","GET"])
@login_required
def update_course(id):
    if current_user.role=="admin":
        course=Course.query.filter_by(id=id).first()
        if request.method=="POST":
            course_name=request.form.get("course_name")
            credit=request.form.get("credit")
            course.name=course_name
            course.credit=credit
            flash("Update complete",category="success")
        return render_template("admin/update_course.html",user=current_user,course=course)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/delete-course/<int:id>",methods=["POST","GET"])
@login_required
def delete_course(id):
    if current_user.role=="admin":
        course=Course.query.filter_by(id=id).first()
        db.session.delete(course)
        db.session.commit()
        return redirect(url_for("views.view_course"))
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/student-transcript/<int:id>")
@login_required
def student_transcript(id):
    if current_user.role=="admin":
        student=Students.query.filter_by(id=id).first()
        mark_certificate=Marks.query.filter_by(student_id=student.id, level="certificate_track").all()
        mark_diploma=Marks.query.filter_by(student_id=student.id, level="diploma_track").all()
        avgs=[]

        if mark_certificate:
            credit=0
            mark1=0
            mark2=0
            for i in mark_certificate:
                credit+=i.course.credit
                if i.semister=="1st":
                    mark1+=i.total
                else:
                    mark2+=i.total
            avg=(round((mark1/credit),2),round((mark2/credit),2))
            avgs.append(avg)

        if mark_diploma:
            credit=0
            mark1=0
            mark2=0
            for i in mark_diploma:
                credit+=i.course.credit
                if i.semister=="1st":
                    mark1+=i.total
                else:
                    mark2+=i.total
            avg=(round((mark1/credit),2),round((mark2/credit),2))
            avgs.append(avg)

        return render_template("admin/student_transcript.html",
                            user=current_user,
                            student=student,
                            mark_100=mark_certificate,
                            mark_200=mark_diploma,
                            avgs=avgs)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/convert-to-pdf/<int:id>",methods=["GET","POST"])
@login_required
def convert(id):
    if current_user.role=="admin":
        student=Students.query.filter_by(id=id).first()
        mark_certificate=Marks.query.filter_by(student_id=student.id, level="certificate_track").all()
        mark_diploma=Marks.query.filter_by(student_id=student.id, level="diploma_track").all()
        avgs=[]
        header=["Course","Credit Hours","Marks"]
        temp_folder=tempfile.gettempdir()
        output=os.path.join(temp_folder,f"{student.firstname}transcript.pdf")
        pdf.add_page()
        pdf.set_font("Arial",size=12)
        info(id=str(student.std_id),
             name=f"{student.lastname} {student.firstname}",
             gender=student.gender,
             dob=student.dob,
             pob=student.pob,
             nationality=student.nationality,
             admission_date=student.admisision_date
             )
        pdf.ln(20)
        pdf.set_font("Arial",style="B",size=12)
        pdf.cell(190,7,"Student Transcript",align="C")
        pdf.set_font("Arial",size=12)
        pdf.ln(10)

        if mark_certificate:
            credit=0
            mark1=0
            mark2=0
            marks_1st=[]
            marks_2nd=[]
            for i in mark_certificate:
                credit+=i.course.credit
                if i.semister=="1st":
                    mark1+=i.total
                    tp=(i.course.name,str(i.course.credit),str(i.total))
                    marks_1st.append(tp)
                else:
                    mark2+=i.total
                    tp=(i.course.name,str(i.course.credit),str(i.total))
                    marks_2nd.append(tp)

            avg=(round((mark1/credit),2),round((mark2/credit),2))
            avgs.append(avg)
            pdf.cell(190,7,"Certificate Track- 1st Semister",align="L")
            pdf.ln(8)
            table=PDFWithTable()
            table.add_table(header,marks_1st)
            pdf.ln(1)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(180,7,f"Wieghted Average: {avgs[0][0]}",0,0,"L",True)
            pdf.ln(30)
            pdf.cell(190,7,"Certificate Track- 2nd Semister",align="L")
            pdf.ln(8)
            table=PDFWithTable()
            table.add_table(header,marks_2nd)
            pdf.ln(1)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(180,7,f"Wieghted Average: {avgs[0][1]}",0,0,"L",True)

        if mark_diploma:
            credit=0
            mark1=0
            mark2=0
            marks_1st=[]
            marks_2nd=[]
            pdf.add_page()
            pdf.set_font("Arial",size=12)

            for i in mark_diploma:
                credit+=i.course.credit
                if i.semister=="1st":
                    mark1+=i.total
                    tp=(i.course.name,str(i.course.credit),str(i.total))
                    marks_1st.append(tp)
                else:
                    mark2+=i.total
                    tp=(i.course.name,str(i.course.credit),str(i.total))
                    marks_2nd.append(tp)

            avg=(round((mark1/credit),2),round((mark2/credit),2))
            avgs.append(avg)
            pdf.cell(190,7,"Certificate Track- 1st Semister",align="L")
            pdf.ln(8)
            table=PDFWithTable()
            table.add_table(header,marks_1st)
            pdf.ln(1)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(180,7,f"Wieghted Average: {avgs[1][0]}",0,0,"L",True)
            pdf.ln(30)
            pdf.cell(190,7,"Certificate Track- 2nd Semister",align="L")
            pdf.ln(8)
            table=PDFWithTable()
            table.add_table(header,marks_2nd)
            pdf.ln(1)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(180,7,f"Wieghted Average: {avgs[1][1]}",0,0,"L",True)

        pdf.output(output)
        return send_file(output,as_attachment=True)
        
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/update/<int:id>",methods=["POST","GET"])
@login_required
def update(id):
    if current_user.role=="admin":
        student=Students.query.filter_by(id=id).first()
        if request.method=="POST":
                std_id=request.form.get("std-id")
                firstname=request.form.get("firstname")
                lastname=request.form.get("lastname")
                dob=request.form.get("dob")
                gender=request.form.get("gender")
                pob=request.form.get("pob")
                nationality=request.form.get("nationality")
                admission_date=request.form.get("admission-date")
                current_track=request.form.get("track")

                if len(std_id)==0:
                    flash("Student ID is empty",category="error")
                elif len(firstname)==0:
                    flash("First Name is empty",category="error")
                elif len(lastname)==0:
                    flash("Last Name is empty",category="error")
                elif len(dob)==0:
                    flash("Date of Birth is empty",category="error")
                elif len(pob)==0:
                    flash("Place of Birth is empty",category="error")
                elif len(nationality)==0:
                    flash("Nationality is empty",category="error")
                elif len(admission_date)==0:
                    flash("Admission Date  is empty",category="error")
                else:
                    student.std_id=std_id
                    student.firstname=firstname
                    student.lastname=lastname
                    student.dob=dob
                    student.pob=pob
                    student.nationality=nationality
                    student.admission_date=admission_date
                    student.current_track=current_track
                    db.session.commit()
                    flash("Update Complete",category="success")

        return render_template("admin/update.html",user=current_user,student=student)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/delete/<int:id>",methods=["POST","GET"])
@login_required
def delete(id):
    if current_user.role=="admin":
        student=Students.query.filter_by(id=id).first()
        db.session.delete(student)
        db.session.commit()
        return redirect(url_for("views.dashboard"))
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))
    
@views.route("/promote",methods=["POST","GET"])
@login_required
def promote():
    if current_user.role=="admin":
        students=Students.query.all()
        if request.method=="POST":
            li=request.form.getlist("check")
            for id in li:
                student=Students.query.filter_by(id=id).first()
                if student.current_track=="certificate_track":
                    student.current_track="diploma_track"
                    db.session.commit()
                    flash("Promoted",category="success")
                elif student.current_track=="diploma":
                    student.current_track=="completed"
                    db.session.commit()
                    flash("Promoted",category="success")

                else:
                    flash(f"{student.firstname} {student.lastname} has completed")
        return render_template("admin/promote.html",user=current_user,students=students)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))
    
@views.route("/search-promote",methods=["POST","GET"])
@login_required
def search_promote():
    if current_user.role=="admin":
        search=request.form.get('search')
        aspect=request.form.get('aspect')
        std_li=[]

        if aspect=="all":
            std_li=Students.query.all()
        elif aspect=="firstname":
            students=Students.query.filter_by(firstname=search).all()
            std_li=students
        elif aspect=="lastname":
            students=Students.query.filter_by(lastname=search).all()
            std_li=students
        elif aspect=="std_id":
            students=Students.query.filter_by(std_id=search).all()
            std_li=students
        elif aspect=="current_track":
            if search.lower() in "certificate_track":
                students=Students.query.filter_by(current_track="certificate_track").all()
                std_li=students
            elif search.lower() in "diploma_track":
                students=Students.query.filter_by(current_track="diploma_track").all()
                std_li=students

        if request.method=="POST":
            li=request.form.getlist("check")
            for id in li:
                student=Students.query.filter_by(id=id).first()
                if student.current_track=="certificate_track":
                    student.current_track="diploma_track"
                    db.session.commit()
                    flash("Promoted",category="success")
                elif student.current_track=="diploma":
                    student.current_track=="completed"
                    db.session.commit()
                    flash("Promoted",category="success")

                else:
                    flash(f"{student.firstname} {student.lastname} has completed")
        return render_template("admin/search_promote.html",user=current_user,students=std_li)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))
    
@views.route("/account", methods=["GET","POST"])
@login_required
def account():
    if current_user.role=="admin":
        courses=Course.query.all()
        if request.method=="POST":
            name=request.form.get("name")
            email=request.form.get("email")
            role=request.form.get("role")
            course=request.form.get("course")
            password=request.form.get("password")

            if len(name)==0:
                flash("Name is empty!",category="error")
            elif len(email)==0:
                flash("Email is empty!",category="error")
            elif len(password)<=4:
                flash("Password is to short!",category="error")
            else:
                user=User.query.filter_by(id=current_user.id).first()
                user.name=name
                user.email=email
                user.role=role
                user.course=course
                user.password=password

                db.session.commit()
                flash("Updated successfully",category="success")
        return render_template("admin/account.html",user=current_user,courses=courses)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))


#########################################################
# teachers
def get_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if target_value in value:
            return key
    return None

def get_students_id():
    li=[]
    students_id=db.session.query(Course.name)
    for id in students_id:
        li.append(id[0])
    return li

def get_course(target,track):
    li=[]
    students=Students.query.all()
    for student in students:
        if student.current_track==track:
            for course in student.offers:
                if course.name==target:
                    li.append(student)
    return li

@views.route("/semister-level",methods=["GET","POST"])
@login_required
def semister_level():
    if current_user.role=="teacher":
        if request.method=="POST":
            session["semister"]=request.form.get("semister")
            session["track"]=request.form.get("track")
            return redirect(url_for("views.tch_dashboard"))
        return render_template("teachers/semister_level.html",user=current_user)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))

@views.route("/tch-dashboard",methods=["GET","POST"])
@login_required
def tch_dashboard():
    if current_user.role=="teacher":
        print(session["track"])
        students=get_course(current_user.course,session["track"])
        course=Course.query.filter_by(name=current_user.course).first()
        marks=[]
        for student in students:
            mark=Marks.query.filter_by(student_id=student.id,course_id=course.id).first()
            if mark:
                marks.append(mark)


        print(students)
        if request.method=="POST":
            for student in students:
                mid=request.form.get(f"{student.id}mid")
                exam=request.form.get(f"{student.id}exam")
                total=int(mid) + int(exam)
                grade=get_key_by_value(grade_range,total)
                
                for i in student.offers:
                    mark=Marks.query.filter_by(student_id=student.id,course_id=i.id).first()
                    if mark:
                        mark.mid=mid
                        mark.exam=exam
                        db.session.commit()
                    else:
                        if i.name==current_user.course:
                            mark=Marks(semister=session["semister"],level=session["track"] ,mid=mid,exam=exam,total=total,grade=grade,course_id=i.id,student_id=student.id)
                            db.session.add(mark)
                            db.session.commit()
                    
                db.session.commit()
            flash("Form submited Successfully",category="success")

        return render_template("teachers/tch_dashboard.html",user=current_user,students=students,marks=marks)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))
    
@views.route("/tch_account", methods=["GET","POST"])
@login_required
def tch_account():
    if current_user.role=="teacher":
        courses=Course.query.all()
        if request.method=="POST":
            name=request.form.get("name")
            email=request.form.get("email")
            role=request.form.get("role")
            course=request.form.get("course")
            password=request.form.get("password")

            if len(name)==0:
                flash("Name is empty!",category="error")
            elif len(email)==0:
                flash("Email is empty!",category="error")
            elif len(password)<=4:
                flash("Password is to short!",category="error")
            else:
                user=User.query.filter_by(id=current_user.id).first()
                user.name=name
                user.email=email
                user.role=role
                user.course=course
                user.password=password

                db.session.commit()
                flash("Updated successfully",category="success")
        return render_template("teachers/tch_account.html",user=current_user,courses=courses)
    else:
        flash("You do not have access to this page!",category="error")
        return redirect(url_for("auth.logout"))