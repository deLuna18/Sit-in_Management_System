from flask import Flask, render_template, request, redirect, flash, session, make_response, url_for
import dbhelper, os
from werkzeug.utils import secure_filename
from PIL import Image  


app = Flask(__name__)
app.secret_key = "deluna"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def disable_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/")
def home():
    if "user" in session:
        return redirect("/student_dashboard")
    return redirect("/student_login")

# UPLOAD PROFILE PICTURE
@app.route("/upload_profile_picture", methods=["POST"])
def upload_profile_picture():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect("/student_login")

    if "file" not in request.files:
        flash("No file selected.", "danger")
        return redirect("/student_dashboard")

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "danger")
        return redirect("/student_dashboard")

    if file and allowed_file(file.filename):
        if file.content_length > 2 * 1024 * 1024:  
            flash("File size exceeds 2MB limit.", "danger")
            return redirect("/student_dashboard")

        filename = secure_filename(f"{session['user']}_{file.filename}")
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        image = Image.open(file)
        image.thumbnail((300, 300)) 
        image.save(file_path)

        dbhelper.update_profile_picture(session["user"], filename)
        flash("Profile picture updated!", "success")
        return redirect("/student_dashboard")

    flash("Invalid file type. Allowed: png, jpg, jpeg, gif", "danger")
    return redirect("/student_dashboard")


# LOGIN STUDENT
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = dbhelper.get_username(username)  

        if user and user[0]["password"] == password:
            session["user"] = username
            session['logged_in'] = True
            flash("Login successful!", "success")  
            return redirect("/student_dashboard")
        flash("Invalid username or password.", "danger") 
        return redirect("/student_login")

    return render_template("student_login.html")

# REGISTRATION
@app.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        idno = request.form["idno"]
        lastname = request.form["lastname"]
        firstname = request.form["firstname"]
        middlename = request.form["middlename"]
        course = request.form["course"]
        year_level = request.form["year_level"]
        email_address = request.form["email_address"]
        username = request.form["username"]
        password = request.form["password"]  
        success = dbhelper.register_user(lastname, firstname, middlename, course, year_level, email_address, username, password)  

        if success:
            flash("Registration successful! Please login.", "success")
            return redirect("/student_login")
        else:
            flash("Username already exists. Please try again with a different username.", "danger")

    return render_template("student_register.html")

# STUDENT DASBOARD
@app.route("/student_dashboard")
def student_dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect("/student_login")
    
    student_info = dbhelper.get_student_by_username(session["user"])

    if not student_info:
        flash("User not found!", "danger")
        return redirect("/student_login")

    return render_template("student_dashboard.html", student=student_info)

# STAFF DASHBOARD
@app.route("/staff_dashboard")
def staff_dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect("/student_login")
    staff_list = dbhelper.get_all_staff()
    return render_template("staff_dashboard.html", username=session["user"], staff_list=staff_list)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect("/student_login")

    student_info = dbhelper.get_student_by_username(session["user"])
    if not student_info:
        flash("User not found!", "danger")
        return redirect("/student_login")

    student_info.setdefault("profile_picture", "default-profile.png")

    if request.method == 'POST':
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        course = request.form['course']
        year_level = request.form['year_level']
        email_address = request.form['email_address']
        address = request.form['address']

        file = request.files.get("profile_image")
        profile_picture = student_info["profile_picture"]

        if file and allowed_file(file.filename):
            filename = secure_filename(f"{session['user']}_{file.filename}")
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            profile_picture = filename

        dbhelper.update_student_profile(session["user"], firstname, middlename, lastname, 
                                        course, year_level, email_address, address, profile_picture)

        flash("Profile updated successfully!", "success")
        return redirect("/student_dashboard")

    return render_template("edit_profile.html", student=student_info)




# LOGOUT FOR STUDENTS
@app.route("/logout")
def logout():
    flash("Logout Successfully", "success")
    session.pop("user", None)
    return redirect("/student_login")

if __name__ == "__main__":
    app.run(debug=True)
