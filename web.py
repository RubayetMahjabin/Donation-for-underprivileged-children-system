from flask import Flask, render_template, request, session, redirect, url_for
from datetime import date,time, datetime
from werkzeug.utils import secure_filename
import sqlite3 as sql
import os
# Create Database if it doesnt exist
if not os.path.isfile('database.db'):
  conn = sql.connect('database.db')
  conn.execute('CREATE TABLE IF NOT EXISTS Donors (Name TEXT NOT NULL, Amount INTEGER NOT NULL, Email TEXT NOT NULL, [timestamp] TIMESTAMP)')
  conn.execute('CREATE TABLE IF NOT EXISTS Users (Name TEXT NOT NULL, Email TEXT NOT NULL, Password TEXT NOT NULL, Contact INTEGER NOT NULL)')
  conn.execute('CREATE TABLE IF NOT EXISTS Admins (Username TEXT UNIQUE NOT NULL, Password TEXT NOT NULL)')
  
  ############################### Volunteer DATABASE #########################
  conn.execute('CREATE TABLE IF NOT EXISTS Volunteers (Name TEXT NOT NULL, Email TEXT NOT NULL, Password TEXT NOT NULL, Contact INTEGER NOT NULL)')
  conn.execute('CREATE TABLE IF NOT EXISTS Volunteer_Rating (volunteerName TEXT NOT NULL,  rating Text NOT NULL, comment TEXT NOT NULL)')
  conn.execute('CREATE TABLE IF NOT EXISTS VolunteerExperience (Name TEXT UNIQUE NOT NULL, Experience TEXT NOT NULL)')
  
  
  conn.execute('CREATE TABLE IF NOT EXISTS Projects (ID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT NOT NULL, Description TEXT NOT NULL, GoalAmount INTEGER NOT NULL, Image TEXT NOT NULL)')
  conn.execute('CREATE TABLE IF NOT EXISTS Stories (ID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT NOT NULL, Content TEXT NOT NULL, Image TEXT NOT NULL)')
  conn.execute('CREATE TABLE IF NOT EXISTS Likes (ID INTEGER PRIMARY KEY AUTOINCREMENT, StoryID INTEGER, UserID INTEGER)')
  conn.execute('CREATE TABLE IF NOT EXISTS Comments (ID INTEGER PRIMARY KEY AUTOINCREMENT, StoryID INTEGER, UserID INTEGER, Content TEXT NOT NULL)')
  conn.execute('CREATE TABLE IF NOT EXISTS Campaigns (ID INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT NOT NULL, Content TEXT NOT NULL)')
  conn.execute('INSERT INTO Admins (Username, Password) VALUES (?, ?)', ('Rubayetadmin1', 'admin123456'))
  conn.commit()
  conn.close()

web = Flask(__name__,static_url_path='/assets',
            static_folder='assets', 
            template_folder='templates')

UPLOAD_FOLDER = 'assets/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

web.secret_key = "amoni_secret_key_rubayet" 


web.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@web.route('/')
def root():
   session['logged_out']= 1
   return render_template('index.html')

@web.route('/index.html')
def index():
   return render_template('index.html')

@web.route('/welcome_page.html')
def welcome_page():
   return render_template('welcome_page.html')

@web.route('/menuBar.html')
def menu_bar():
   return render_template('menuBar.html')

@web.route('/footer.html')
def footer():
   return render_template('footer.html')



@web.route('/contact.html')
def contact():
   return render_template('contact.html')

@web.route('/our-causes.html')
def our_causes():
   return render_template('our-causes.html')

@web.route('/about-us.html')
def about_us():
   return render_template('about-us.html')


############################ Top 3 donations #####################################3

# Function to fetch top 3 donors
def get_top_donors():
    conn = sql.connect('database.db')  
    cursor = conn.cursor()

    # Fetch top 3 donors based on Amount
    query = "SELECT Name FROM Donors ORDER BY Amount DESC LIMIT 3"
    cursor.execute(query)
    top_donors = cursor.fetchall()

    conn.close()

    return top_donors

# Route to display top donors in HTML
@web.route('/top_donators.html')
def top_donators():
    top_donors = get_top_donors()
    return render_template('top_donators.html', top_donors=top_donors)


####################################### VOLUNTEER ########################

####################### Volunteer Register #############################################
@web.route('/volunteer_register', methods=['GET', 'POST'])
def volunteer_register():
  if request.method == 'POST':
    nm = request.form['nm']
    contact = request.form['contact']
    email = request.form['email']
    password = request.form['password']
         
    with sql.connect("database.db") as con:
      cur = con.cursor()
      #check if Volunteer already present
      cur.execute("SELECT Email FROM Volunteers WHERE Email=(?)",[(email)])
      data = cur.fetchall()
      if len(data)>0:
        print('Volunteer already exists')
        volunteer_exists=1
      else:
        print("Volunteer not found, register new Volunteer")
        volunteer_exists=0
        cur.execute("INSERT INTO Volunteers (Name,Email,Password,Contact) VALUES (?,?,?,?)",(nm,email,password,contact) )
        con.commit()

  return render_template('volunteer_login.html',volunteer_exists=volunteer_exists, invalid = None, logged_out=None)

@web.route('/volunteer_dashboard.html')
def volunteer_dashboard():
    return render_template('volunteer_dashboard.html')



############################# Volunteer Login ##################
@web.route('/volunteer_login.html',  methods=['GET', 'POST'])
def volunteer_login():
  invalid = None
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']     
    with sql.connect("database.db") as con:
      cur = con.cursor()
      #Validate volunteer credentails from database
      cur.execute("SELECT Email FROM Volunteers WHERE Email=(?) AND Password=(?)",[(email),(password)])
      con.commit()
      data = cur.fetchall()
      if len(data)>0:
        print('Login Success')
        # Fetch name of user
        cur.execute("SELECT Name FROM Volunteers WHERE Email=(?) AND Password=(?)",[(email),(password)])
        nm = cur.fetchall()
        nm=nm[0][0]
        # Store User details in Session and log in user
        session['nm'] = nm
        session['email'] = email
        session['logged_out'] = None
        return redirect(url_for('volunteer_dashboard'))
      else:
        print("Invalid Login")
        invalid=1  
  return render_template('volunteer_login.html',volunteer_exists=None, invalid = invalid, logged_out=None)

############################ volunteer Logout ######################

@web.route('/volunteer_logout')
def volunteer_logout():
  session.clear()
  session['logged_out']=1
  print('Session Cleared and Logged Out')
  return render_template('index.html') 


@web.route('/volunteer_resource.html')
def volunteer_resource():
   return render_template('volunteer_resource.html')

@web.route('/exp_display.html')
def view_experiences():
    conn = sql.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM VolunteerExperience')
    experiences = cursor.fetchall()
    conn.close()
    return render_template('exp_display.html', experiences=experiences)


@web.route('/volunteer_exp_input.html')
def volunteer_exp_input():
    return render_template('volunteer_exp_input.html')

@web.route('/submit', methods=['POST'])
def submit():
    Name = request.form.get('Name')
    Experience = request.form.get('Experience')

    if Name and Experience:
        conn = sql.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO VolunteerExperience (Name, Experience) VALUES (?, ?)', (Name, Experience))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        return "Name and Experience fields are required."
    


@web.route('/volunteer_rating.html')
def volunteer_rating():
    return render_template('volunteer_rating.html')

# This route handles the form submission
@web.route('/submit_rating', methods=['POST'])
def submit_rating():
    volunteerName = request.form.get('volunteerName')
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')

    # Connecting to the SQLite database
    conn = sql.connect('database.db')
    cursor = conn.cursor()

    # Inserting the data into the table
    cursor.execute("INSERT INTO Volunteer_Rating (volunteerName, rating, comment) VALUES (?, ?, ?)",
                   (volunteerName, rating, comment))

    # Committing the changes and closing the connection
    conn.commit()
    conn.close()


    return "Rating submitted successfully!"



####################### User Register #############################################
@web.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    nm = request.form['nm']
    contact = request.form['contact']
    email = request.form['email']
    password = request.form['password']
         
    with sql.connect("database.db") as con:
      cur = con.cursor()
      #check if User already present
      cur.execute("SELECT Email FROM Users WHERE Email=(?)",[(email)])
      data = cur.fetchall()
      if len(data)>0:
        print('User already exists')
        user_exists=1
      else:
        print("User not found, register new user")
        user_exists=0
        cur.execute("INSERT INTO Users (Name,Email,Password,Contact) VALUES (?,?,?,?)",(nm,email,password,contact) )
        con.commit()

  return render_template('login.html',user_exists=user_exists, invalid = None, logged_out=None)

############################# User Login ##################
@web.route('/login.html',  methods=['GET', 'POST'])
def login():
  invalid = None
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']     
    with sql.connect("database.db") as con:
      cur = con.cursor()
      #Validate user credentails from database
      cur.execute("SELECT Email FROM Users WHERE Email=(?) AND Password=(?)",[(email),(password)])
      con.commit()
      data = cur.fetchall()
      if len(data)>0:
        print('Login Success')
        # Fetch name of user
        cur.execute("SELECT Name FROM Users WHERE Email=(?) AND Password=(?)",[(email),(password)])
        nm = cur.fetchall()
        nm=nm[0][0]
        # Store User details in Session and log in user
        session['nm'] = nm
        session['email'] = email
        session['logged_out'] = None
        return redirect(url_for('user_dashboard'))
      else:
        print("Invalid Login")
        invalid=1  
  return render_template('login.html',user_exists=None, invalid = invalid, logged_out=None)

############################ User Logout ######################

@web.route('/logout')
def logout():
  session.clear()
  session['logged_out']=1
  print('Session Cleared and Logged Out')
  return render_template('index.html') 


################# Admin dashboard ####################
@web.route('/admin_dashboard.html')
def admin_dashboard():
    if 'admin_id' in session:
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('admin_login'))

########################### Managing user accounts and deletions #####################################################

@web.route('/admin_manage_users.html')
def admin_manage_users():
    if 'admin_id' in session:
        # Fetch user accounts from the database (example)
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Users")
            user_accounts = cur.fetchall()

        return render_template('admin_manage_users.html', user_accounts=user_accounts)
    else:
        return redirect(url_for('admin_login'))
    
########################### ADMIN DELETE USER ############################
    

@web.route('/delete_user/<email>', methods=['GET'])
def delete_user(email):
    if 'admin_id' in session:
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Users WHERE Email = ?", (email,))
            con.commit()
        
        return redirect(url_for('admin_manage_users'))
    else:
        return redirect(url_for('admin_login'))
    


##################### viewing donation histories ##############
@web.route('/admin_donations.html')
def admin_donations():
    if 'admin_id' in session:
        # Fetch donation histories from the database (example)
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Donors")
            donation_histories = cur.fetchall()

        return render_template('admin_donations.html', donation_histories=donation_histories)
    else:
        return redirect(url_for('admin_login'))


############################### ADMIN LOGIN ##########################


@web.route('/admin_login.html', methods=['GET', 'POST'])
def admin_login():
    invalid = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Admins WHERE Username = ? AND Password = ?", (username, password))
            admin = cur.fetchone()

            if admin:
                session['admin_id'] = admin[0]  # Store admin ID in the session
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            else:
                invalid = True

    return render_template('admin_login.html', invalid=invalid)

########################### ADMIN LOGOUT ######################

@web.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)  # Remove admin_id from the session
    return redirect(url_for('index'))  # Redirect to the homepage or another page







########################## Admin Post Project ###############################


@web.route('/admin_post_project.html', methods=['GET', 'POST'])
def admin_post_project():
    if request.method == 'POST':
        project_title = request.form['project_title']
        project_description = request.form['project_description']
        project_goal = int(request.form['project_goal'])
        
        if 'project_image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['project_image']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
            
            # Store project details in the database
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Projects (title, description, goal, image) VALUES (?, ?, ?, ?)",
                            (project_title, project_description, project_goal, filename))
                con.commit()
                flash('Project posted successfully!')
    
    return render_template('admin_post_project.html')

##########################ONGOING PROJECTS#####################

@web.route('/project.html')
def project():
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Projects")  # Fetch project data from the Projects table
        projects = cur.fetchall()
    return render_template('project.html', projects=projects)




@web.route('/post_project', methods=['GET', 'POST'])
def post_project():
    if request.method == 'POST':
        # Get the form data
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        goal_amount = request.form.get('goal_amount', '')

        # Check if the required fields are not empty
        if title and description and goal_amount:
            # Insert the project details into the database
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Projects (Title, Description, GoalAmount) VALUES (?, ?, ?)",
                            (title, description, goal_amount))
                con.commit()

            # Redirect to the project page or another appropriate page
            return redirect(url_for('project'))

    # For GET requests or invalid form data, render the admin_post_project.html template
    return render_template('admin_post_project.html')


# Route for user dashboard
@web.route('/user_dashboard.html')
def user_dashboard():
    return render_template('user_dashboard.html')


@web.route('/donate.html')
def donate():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   nm = session['nm']
   email = session['email']
   return render_template('donate.html',nm=nm,email=email)         

#insert values into table
@web.route('/donation',methods = ['POST', 'GET'])
def donation():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   if request.method == 'POST':
         nm = session['nm']
         email = session['email']
         amt = request.form['amt']
         today = datetime.now()
         today = today.strftime("%d-%m-%Y"+","+"%H:%M")
         
         with sql.connect("database.db") as con:
            cur = con.cursor()
            #check if already donated. If already donated, add donation. Else create new donation
            cur.execute("SELECT Email FROM Donors WHERE Email=(?)",[(email)])
            data = cur.fetchall()
            if len(data)>0:
              cur.execute("UPDATE Donors SET Amount=Amount+(?) WHERE Email=(?)",[(amt),(email)])
            else:
              cur.execute("INSERT INTO Donors (Name,Amount,Email,timestamp) VALUES (?,?,?,?)",(nm,amt,email,today) )                
            con.commit()
            
            # Greeting
            msg = "Thank You for Donating"
            for row in cur.execute("SELECT Amount FROM Donors WHERE Email=(?)",[(email)]):
                Amount=row
         return render_template("greeting.html",msg = msg,nm=nm,Amount=Amount,today=today, email=email)




#Display List of Donations
@web.route('/list1.html')
def list1():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("SELECT * FROM Donors")
   
   rows = cur.fetchall()
   return render_template("list1.html",rows = rows)

######################Display Profile#####################

@web.route('/profile.html')
def profile():
   # If Logged Out, Redirect to Log In page
   if session['logged_out']:
    return render_template('login.html',logged_out=1,user_exists=None, invalid = None)
   nm = session['nm']
   email = session['email']
   with sql.connect("database.db") as con:
    cur = con.cursor()
    # Fetch details of user
    cur.execute("SELECT Contact FROM Users WHERE Email=(?)",[(email)])
    contact = cur.fetchall()
    contact=contact[0][0]

    cur.execute("SELECT Password FROM Users WHERE Email=(?)",[(email)])
    password = cur.fetchall()
    password=password[0][0]
   return render_template("profile.html",nm=nm,email=email,contact=contact,password=password)

@web.route('/admin_share_story.html', methods=['POST'])
def admin_share_story():
    if 'admin_id' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            image = request.files['image']
            
            if image.filename == '':
                flash('No selected image')
                return redirect(request.url)
            
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(web.config['UPLOAD_FOLDER'], filename))
                
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO Stories (Title, Content, Image) VALUES (?, ?, ?)",
                                (title, content, filename))
                    con.commit()
                    flash('Story shared successfully!')
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('admin_login'))
    
@web.route('/like_story/<story_id>', methods=['POST'])
def like_story(story_id):
    if 'email' in session:
        user_email = session['email']
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Likes (StoryID, UserID) VALUES (?, ?)",
                        (story_id, user_email))
            con.commit()
    return redirect(url_for('view_story', story_id=story_id))


@web.route('/comment_story/<story_id>', methods=['POST'])
def comment_story(story_id):
    if 'email' in session:
        user_email = session['email']
        content = request.form['content']
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Comments (StoryID, UserID, Content) VALUES (?, ?, ?)",
                        (story_id, user_email, content))
            con.commit()
    return redirect(url_for('view_story', story_id=story_id))

@web.route('/awareness_campaigns.html')
def awareness_campaigns():
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Campaigns")
        campaigns = cur.fetchall()
    return render_template('awareness_campaigns.html', campaigns=campaigns)




# Route to send notifications
@web.route('/admin_send_notification.html', methods=['GET', 'POST'])
def admin_send_notification():
    if request.method == 'POST':
        notification_message = request.form['notification']

        # Notify users (for demonstration, using flash messages)
        flash(f'Notification sent: {notification_message}', 'success')

        # Redirect to admin dashboard or another appropriate page
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_send_notification.html')



web.run(debug=True)


if __name__ == '__main__':
   web.run(debug=True)