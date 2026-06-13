from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from MySQLdb.cursors import DictCursor
from flask import send_from_directory
from flask import Flask
from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv
from flask_mail import Message
from flask import flash
from flask import jsonify
import random



import os

load_dotenv()

app = Flask(__name__)

app.config.from_pyfile("config.py")

mail = Mail(app)

UPLOAD_FOLDER = 'uploads'

@app.route('/download/<filename>')
def download_pdf(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.secret_key = "EduBridge_secret_key"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'EduBridge'

mysql = MySQL(app)




app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)
@app.route('/test-mail')
def test_mail():

    msg = Message(
        'EduBridge Test',
        sender=app.config['MAIL_USERNAME'],
        recipients=[app.config['MAIL_USERNAME']]
    )

    msg.body = 'Email configuration is working.'

    mail.send(msg)

    return "Email Sent Successfully"



@app.route('/send-email-otp', methods=['POST'])
def send_email_otp():

    data = request.get_json()
    email = data['email']

    otp = str(random.randint(100000,999999))

    session['email_otp'] = otp

    msg = Message(
        'EduBridge OTP Verification',
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )

    msg.body = f"""
Welcome to EduBridge

Your OTP is: {otp}

Do not share this OTP.
"""

    try:
        mail.send(msg)
        return "OTP Sent Successfully"

    except Exception as e:
        return str(e)

@app.route('/verify-email-otp', methods=['POST'])
def verify_email_otp():
    return "Email Verified"




#home
@app.route('/')
def home():
    return render_template('home.html')

#login Choice
@app.route('/login-choice')
def login_choice():
    return render_template('login_choice.html')

#student_signup
@app.route('/student-signup', methods=['GET','POST'])
def student_signup():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        password = request.form['password']
        university = request.form['university']
        college_code = request.form['college_code']
        education = request.form['education']
        branch = request.form['branch']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        enrollment = request.form['enrollment']

        cur = mysql.connection.cursor()

        # Check if email already exists
        cur.execute(
            "SELECT id FROM students WHERE email=%s",
            (email,)
        )

        existing_user = cur.fetchone()

        if existing_user:

            flash(
                "This email is already registered. Please login.",
                "error"
            )

            cur.close()

            return redirect('/student-signup')

        # Insert new student
        cur.execute("""
        INSERT INTO students
        (
            name,
            email,
            contact,
            password,
            university_name,
            college_code,
            education,
            branch,
            country,
            state,
            city,
            enrollment_no
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            name,
            email,
            contact,
            password,
            university,
            college_code,
            education,
            branch,
            country,
            state,
            city,
            enrollment
        ))

        mysql.connection.commit()
        cur.close()

        flash(
            "Student account created successfully.",
            "success"
        )

        return redirect('/student-login')

    return render_template('student_signup.html')

#student_login
@app.route('/student-login', methods=['GET','POST'])
def student_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("""
        SELECT id,name
        FROM students
        WHERE email=%s AND password=%s
        """,(email,password))

        student = cur.fetchone()

        if student:

            session['student_id'] = student[0]
            session['student_name'] = student[1]

            flash(
                f"Welcome to EduBridge, {student[1]}!",
                "success"
            )

            return redirect('/')

        else:

            flash(
                "Invalid Email or Password",
                "error"
            )

            return redirect('/student-login')

    return render_template('student_login.html')




#investor_signup
@app.route('/investor-signup', methods=['GET','POST'])
def investor_signup():

    if request.method == 'POST':
        name = request.form['name']
        company_name = request.form['company_name']
        role = request.form['role']
        email = request.form['email']
        contact = request.form['contact']
        registration_no = request.form['registration_no']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        about_company = request.form['about_company']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT id FROM investors WHERE email=%s",
            (email,)
        )

        existing = cur.fetchone()

        if existing:
            flash("Email already registered.", "danger")
            return redirect('/investor-signup')

        cur.execute("""
        INSERT INTO investors
        (
            name,
            company_name,
            role_at_company,
            email,
            contact,
            registration_no,
            country,
            state,
            city,
            about_company,
            password
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            name,
            company_name,
            role,
            email,
            contact,
            registration_no,
            country,
            state,
            city,
            about_company,
            password
        ))

        mysql.connection.commit()
        cur.close()

        flash("Investor account created successfully.", "success")

        return redirect('/investor-login')

    return render_template('investor_signup.html')

#investor-login
@app.route('/investor-login', methods=['GET', 'POST'])
def investor_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("""
        SELECT id, company_name
        FROM investors
        WHERE email=%s AND password=%s
        """,(email,password))

        investor = cur.fetchone()

        if investor:

            session['investor_id'] = investor[0]
            session['company_name'] = investor[1]

            flash("Welcome to EduBridge!", "success")

            return redirect('/')

        flash("Invalid Email or Password", "danger")

    return render_template('investor_login.html')

@app.route('/investor-profile', methods=['GET', 'POST'])
def investor_profile():

    if 'investor_id' not in session:
        return redirect('/investor-login')

    cur = mysql.connection.cursor(DictCursor)

    if request.method == 'POST':
        name = request.form['name']
        company_name = request.form['company_name']
        role = request.form['role']
        contact = request.form['contact']
        registration_no = request.form['registration_no']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        about_company = request.form['about_company']

        cur.execute("""
        UPDATE investors
        SET name=%s,
            company_name=%s,
            role_at_company=%s,
            contact=%s,
            registration_no=%s,
            country=%s,
            state=%s,
            city=%s,
            about_company=%s
        WHERE id=%s
        """,
        (
            name,
            company_name,
            role,
            contact,
            registration_no,
            country,
            state,
            city,
            about_company,
            session['investor_id']
        ))

        mysql.connection.commit()

    cur.execute(
        "SELECT * FROM investors WHERE id=%s",
        (session['investor_id'],)
    )

    investor = cur.fetchone()

    cur.close()

    return render_template(
        'investor_profile.html',
        investor=investor
    )

@app.route('/delete-investor-account')
def delete_investor_account():

    if 'investor_id' not in session:
        return redirect('/investor-login')

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM investors WHERE id=%s",
        (session['investor_id'],)
    )

    mysql.connection.commit()
    cur.close()

    session.clear()

    flash(
        "Investor account deleted successfully.",
        "success"
    )

    return redirect('/')

@app.route('/reset-password', methods=['GET','POST'])
def reset_password():

    if 'student_id' not in session:
        return redirect('/student-login')

    if request.method == 'POST':

        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT password FROM students WHERE id=%s",
            (session['student_id'],)
        )

        user = cur.fetchone()

        if user[0] != old_password:
            flash("Current password is incorrect.", "danger")
            return redirect('/reset-password')

        if new_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect('/reset-password')

        cur.execute(
            "UPDATE students SET password=%s WHERE id=%s",
            (new_password, session['student_id'])
        )

        mysql.connection.commit()
        cur.close()

        flash("Password updated successfully.", "success")

        return redirect('/profile')

    return render_template('reset_password.html')

@app.route('/investor-reset-password', methods=['GET', 'POST'])
def investor_reset_password():

    if 'investor_id' not in session:
        return redirect('/investor-login')

    if request.method == 'POST':

        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT password FROM investors WHERE id=%s",
            (session['investor_id'],)
        )

        investor = cur.fetchone()

        if not investor:
            flash("Investor not found.", "danger")
            return redirect('/investor-profile')

        if investor[0] != old_password:
            flash("Current password is incorrect.", "danger")
            return redirect('/investor-reset-password')

        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect('/investor-reset-password')

        cur.execute(
            "UPDATE investors SET password=%s WHERE id=%s",
            (new_password, session['investor_id'])
        )

        mysql.connection.commit()
        cur.close()

        flash("Password updated successfully.", "success")

        return redirect('/investor-profile')

    return render_template('investor_reset_password.html')

from MySQLdb.cursors import DictCursor

@app.route('/investors')
def investors():

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT
            id,name,
            company_name,
            role_at_company,
            city,
            about_company
        FROM investors
        ORDER BY id DESC
    """)

    investors = cur.fetchall()

    cur.close()

    return render_template(
        'investors.html',
        investors=investors
    )

@app.route('/investor/<int:id>')
def investor_details(id):

    cur = mysql.connection.cursor(DictCursor)

    cur.execute(
        "SELECT * FROM investors WHERE id=%s",
        (id,)
    )

    investor = cur.fetchone()

    cur.close()

    if not investor:
        return "Investor Not Found"

    return render_template(
        'investor_details.html',
        investor=investor
    )

@app.route('/logout')
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "warning"
    )

    return redirect('/')


#addProject
@app.route('/add-project', methods=['GET', 'POST'])
def add_project():

    if 'student_id' not in session:
        return redirect('/student-login')

    if request.method == 'POST':

        title = request.form['title']
        short_desc = request.form['short_description']
        detailed_desc = request.form['detailed_description']
        funding = request.form['funding']
        interest = request.form['interest']
        months = request.form['return_months']
        category = request.form['category']

        pdf = request.files['project_pdf']

        filename = ""

        if pdf:
            filename = secure_filename(pdf.filename)

            pdf.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

        cur = mysql.connection.cursor()

        cur.execute("""
        INSERT INTO projects
        (
            student_id,
            title,
            short_description,
            detailed_description,
            funding_required,
            interest,
            return_months,
            category,
            project_pdf
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            session['student_id'],
            title,
            short_desc,
            detailed_desc,
            funding,
            interest,
            months,
            category,
            filename
        ))

        mysql.connection.commit()
        cur.close()
        flash(
    "Project added successfully.",
    "success"
)
        return redirect('/projects')

    return render_template('add_project.html')

@app.route('/projects')
def projects():

    category = request.args.get('category')

    cur = mysql.connection.cursor()

    if category:

        cur.execute("""
        SELECT p.id,
               p.title,
               p.short_description,
               p.funding_required,
               p.interest,
               p.return_months,
               p.category,
               s.name
        FROM projects p
        JOIN students s
        ON p.student_id = s.id
        WHERE p.category = %s
        ORDER BY p.created_at DESC
        """, (category,))

    else:

        cur.execute("""
        SELECT p.id,
               p.title,
               p.short_description,
               p.funding_required,
               p.interest,
               p.return_months,
               p.category,
               s.name
        FROM projects p
        JOIN students s
        ON p.student_id = s.id
        ORDER BY p.created_at DESC
        """)

    data = cur.fetchall()
    cur.close()

    return render_template(
        'view_projects.html',
        projects=data,
        selected_category=category
    )

@app.route('/project/<int:id>')
def project_details(id):

    cur = mysql.connection.cursor(DictCursor)

    # ==========================
    # PROJECT
    # ==========================
    cur.execute("""
        SELECT
            p.*,
            s.name AS owner_name,
            s.email,
            s.contact

        FROM projects p

        LEFT JOIN students s
        ON p.student_id = s.id

        WHERE p.id=%s
    """, (id,))

    project = cur.fetchone()

    if not project:
        cur.close()
        return "Project not found"

    # ==========================
    # STUDENT (OWNER) DETAILS + CONTACT
    # ==========================
    cur.execute("""
        SELECT id, name, email, contact, university_name, city, state
        FROM students
        WHERE id=%s
    """, (project['student_id'],))

    student = cur.fetchone()

    student_name = student['name'] if student else "Unknown"
    student_contact = student['contact'] if student else "N/A"

    # ==========================
    # CONVERSATION ROOM
    # ==========================
    cur.execute("""
        SELECT id
        FROM project_conversations
        WHERE project_id=%s
        LIMIT 1
    """, (id,))

    room = cur.fetchone()

    if room:
        room_id = room['id']
    else:
        cur.execute("""
            INSERT INTO project_conversations
            (project_id, student_id, investor_id)
            VALUES (%s, %s, 0)
        """, (id, project['student_id']))

        mysql.connection.commit()
        room_id = cur.lastrowid

    # ==========================
    # MESSAGES
    # ==========================
    cur.execute("""
        SELECT *
        FROM chat_messages
        WHERE room_id=%s
        ORDER BY created_at ASC
    """, (room_id,))

    messages = cur.fetchall()

    # ==========================
    # INVESTORS CONNECTED
    # ==========================
    cur.execute("""
        SELECT i.id, i.name, i.email, i.contact, i.company_name, i.city, i.state
        FROM project_conversations pc
        JOIN investors i ON pc.investor_id = i.id
        WHERE pc.project_id=%s
        AND pc.investor_id != 0
    """, (id,))

    investors = cur.fetchall()

    # ==========================
    # INVESTOR CONTACT (CURRENT CHAT USER)
    # ==========================
    investor_name = None
    investor_contact = None

    if session.get('investor_id'):
        cur.execute("""
            SELECT name, contact
            FROM investors
            WHERE id=%s
        """, (session['investor_id'],))

        inv = cur.fetchone()

        if inv:
            investor_name = inv['name']
            investor_contact = inv['contact']

    cur.close()

    # ==========================
    # RETURN
    # ==========================
    return render_template(
        "project_details.html",
        project=project,
        student=student,
        student_name=student_name,
        student_contact=student_contact,
        investors=investors,
        investor_name=investor_name,
        investor_contact=investor_contact,
        messages=messages,
        room_id=room_id
    )

@app.route('/delete-account')
def delete_account():

    if 'student_id' not in session:
        return redirect('/student-login')

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM projects WHERE student_id=%s",
        (session['student_id'],)
    )

    cur.execute(
        "DELETE FROM students WHERE id=%s",
        (session['student_id'],)
    )

    mysql.connection.commit()
    cur.close()

    session.clear()

    flash(
        "Account deleted successfully.",
        "warning"
    )

    return redirect('/')


@app.route('/delete-project/<int:id>')
def delete_project(id):

    if 'student_id' not in session:
        return redirect('/student-login')

    cur = mysql.connection.cursor()

    # Delete only if project belongs to logged-in student
    cur.execute("""
        DELETE FROM projects
        WHERE id=%s
        AND student_id=%s
    """, (id, session['student_id']))

    mysql.connection.commit()
    cur.close()

    flash(
        "Project deleted successfully.",
        "warning"
    )

    return redirect('/my-projects')


@app.route('/update-project/<int:id>', methods=['GET','POST'])
def update_project(id):

    if 'student_id' not in session:
        return redirect('/student-login')

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT *
        FROM projects
        WHERE id=%s
        AND student_id=%s
    """,(id,session['student_id']))

    project = cur.fetchone()

    if not project:
        return "Unauthorized Access"

    if request.method == 'POST':

        title = request.form['title']
        short_desc = request.form['short_description']
        detailed_desc = request.form['detailed_description']
        funding = request.form['funding']
        interest = request.form['interest']
        months = request.form['return_months']
        category = request.form['category']

        cur.execute("""
            UPDATE projects
            SET title=%s,
                short_description=%s,
                detailed_description=%s,
                funding_required=%s,
                interest=%s,
                return_months=%s,
                category=%s
            WHERE id=%s
            AND student_id=%s
        """,
        (
            title,
            short_desc,
            detailed_desc,
            funding,
            interest,
            months,
            category,
            id,
            session['student_id']
        ))

        mysql.connection.commit()
        flash(
    "Project updated successfully.",
    "success"
)
        return redirect(f'/project/{id}')

    return render_template(
        'update_project.html',
        project=project
    )

@app.route('/my-projects')
def my_projects():

    if 'student_id' not in session:
        return redirect('/student-login')

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT *
        FROM projects
        WHERE student_id=%s
        ORDER BY id DESC
    """, (session['student_id'],))

    projects = cur.fetchall()

    cur.close()

    return render_template(
        'my_projects.html',
        projects=projects
    )
@app.route('/profile', methods=['GET','POST'])
def profile():

    if 'student_id' not in session:
        return redirect('/student-login')

    cur = mysql.connection.cursor(DictCursor)

    if request.method == 'POST':

        cur.execute("""
        UPDATE students
        SET
            name=%s,
            email=%s,
            contact=%s,
            university_name=%s,
            college_code=%s,
            education=%s,
            branch=%s,
            country=%s,
            state=%s,
            city=%s,
            enrollment_no=%s
        WHERE id=%s
        """,
        (
            request.form['name'],
            request.form['email'],
            request.form['contact'],
            request.form['university'],
            request.form['college_code'],
            request.form['education'],
            request.form['branch'],
            request.form['country'],
            request.form['state'],
            request.form['city'],
            request.form['enrollment'],
            session['student_id']
        ))

        mysql.connection.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect('/profile')

    cur.execute(
        "SELECT * FROM students WHERE id=%s",
        (session['student_id'],)
    )

    student = cur.fetchone()

    cur.close()

    return render_template(
        'profile.html',
        student=student
    )

@app.route('/chat/<int:project_id>')
def chat(project_id):

    if not session.get('student_id') and not session.get('investor_id'):
        return redirect('/login-choice')

    cur = mysql.connection.cursor(DictCursor)

    # =========================
    # GET PROJECT
    # =========================
    cur.execute("""
        SELECT student_id
        FROM projects
        WHERE id=%s
    """, (project_id,))

    project = cur.fetchone()

    if not project:
        cur.close()
        return "Project Not Found"

    student_id = project['student_id']

    # =========================
    # GET STUDENT INFO
    # =========================
    cur.execute("""
        SELECT name, contact
        FROM students
        WHERE id=%s
    """, (student_id,))

    student = cur.fetchone()

    # =========================
    # STUDENT (OWNER) VIEW
    # =========================
    if session.get('student_id') == student_id:

        cur.execute("""
            SELECT 
                cm.id,
                cm.message,
                cm.sender_type,
                cm.sender_id,
                s.name AS student_name,
                s.contact AS student_contact,
                i.name AS investor_name,
                i.contact AS investor_contact
            FROM chat_messages cm
            LEFT JOIN students s 
                ON cm.sender_type='student' AND cm.sender_id = s.id
            LEFT JOIN investors i 
                ON cm.sender_type='investor' AND cm.sender_id = i.id
            JOIN project_conversations pc 
                ON cm.room_id = pc.id
            WHERE pc.project_id=%s
            ORDER BY cm.created_at ASC
        """, (project_id,))

        messages = cur.fetchall()

        cur.close()

        return render_template(
            'chat.html',
            project_id=project_id,
            messages=messages,
            student_name=student['name'],
            student_contact=student['contact']
        )

    # =========================
    # INVESTOR VIEW
    # =========================
    investor_id = session.get('investor_id')

    if investor_id:

        # get investor info
        cur.execute("""
            SELECT name, contact
            FROM investors
            WHERE id=%s
        """, (investor_id,))

        investor = cur.fetchone()

        # get or create conversation
        cur.execute("""
            SELECT id
            FROM project_conversations
            WHERE project_id=%s
            AND investor_id=%s
        """, (project_id, investor_id))

        conversation = cur.fetchone()

        if not conversation:

            cur.execute("""
                INSERT INTO project_conversations
                (project_id, student_id, investor_id)
                VALUES (%s, %s, %s)
            """, (project_id, student_id, investor_id))

            mysql.connection.commit()

            conversation_id = cur.lastrowid

        else:
            conversation_id = conversation['id']

        # =========================
        # GET MESSAGES
        # =========================
        cur.execute("""
            SELECT 
                cm.id,
                cm.message,
                cm.sender_type,
                cm.sender_id,
                s.name AS student_name,
                s.contact AS student_contact,
                i.name AS investor_name,
                i.contact AS investor_contact
            FROM chat_messages cm
            LEFT JOIN students s 
                ON cm.sender_type='student' AND cm.sender_id = s.id
            LEFT JOIN investors i 
                ON cm.sender_type='investor' AND cm.sender_id = i.id
            WHERE cm.room_id=%s
            ORDER BY cm.created_at ASC
        """, (conversation_id,))

        messages = cur.fetchall()

        cur.close()

        return render_template(
            'chat.html',
            project_id=project_id,
            conversation_id=conversation_id,
            messages=messages,
            student_name=student['name'],
            student_contact=student['contact'],
            investor_name=investor['name'],
            investor_contact=investor['contact']
        )

    cur.close()
    return redirect('/login-choice')

@app.route('/send-message/<int:room_id>', methods=['POST'])
def send_message(room_id):

    message = request.form['message']

    cur = mysql.connection.cursor(DictCursor)

    # -------------------------
    # Identify sender
    # -------------------------
    if session.get('student_id'):
        sender_id = session['student_id']
        sender_type = "student"

        cur.execute("""
            SELECT name, contact, email
            FROM students
            WHERE id=%s
        """, (sender_id,))
        sender = cur.fetchone()

    else:
        sender_id = session['investor_id']
        sender_type = "investor"

        cur.execute("""
            SELECT name, contact, email, company_name
            FROM investors
            WHERE id=%s
        """, (sender_id,))
        sender = cur.fetchone()

    # -------------------------
    # Insert message
    # -------------------------
    cur.execute("""
        INSERT INTO chat_messages
        (room_id, sender_id, sender_type, message)
        VALUES (%s, %s, %s, %s)
    """, (room_id, sender_id, sender_type, message))

    mysql.connection.commit()
    cur.close()

    # -------------------------
    # Return FULL sender data
    # -------------------------
    return jsonify({
        "status": "success",
        "message": message,
        "sender_type": sender_type,
        "sender": sender
    })


@app.route('/delete-chat/<int:room_id>')
def delete_chat(room_id):

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM chat_messages
        WHERE room_id=%s
    """, (room_id,))

    mysql.connection.commit()
    cur.close()

    return redirect(request.referrer)

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == "__main__":
    app.run(debug=True)
