from flask import Flask, render_template, request, redirect, flash, session, make_response, url_for
import dbhelper

app = Flask(__name__)
app.secret_key = "deluna"

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
    return render_template("student_dashboard.html", username=session["user"])

# STAFF DASHBOARD
@app.route("/staff_dashboard")
def staff_dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect("/student_login")
    staff_list = dbhelper.get_all_staff()
    return render_template("staff_dashboard.html", username=session["user"], staff_list=staff_list)

# LOGOUT FOR STUDENTS
@app.route("/logout")
def logout():
    flash("Logout Successfully", "success")
    session.pop("user", None)
    return redirect("/student_login")

if __name__ == "__main__":
    app.run(debug=True)
