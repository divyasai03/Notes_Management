from flask import Flask,render_template,redirect,url_for,session,request

import mysql.connector
from werkzeug.security import generate_password_hash,check_password_hash

n=Flask(__name__)
n.secret_key="my secrat key"
db_connect=mysql.connector.connect(host="localhost",user="root",password="mysql@123",database="notes_management")
cursr=db_connect.cursor()
@n.route("/")
def welcome():
    return render_template("login.html")

@n.route("/signup",methods=["GET","POST"])
def register():
    if "username" in session :
        return redirect(url_for("dashboard"))
    
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        p_name=request.form["profile_name"]
        cursr.execute("select * from user_data where username=%s",(username,))
        data1=cursr.fetchone()
        cursr.execute("select * from user_data where profile_name=%s",(p_name,))
        data2=cursr.fetchone()
        if data1:
            return render_template("register.html",info="username already exists plz try other")
        if data2:
            return render_template("register.html",info="profile name  already used plz try other")
        
        hash_password=generate_password_hash(password)
        cursr.execute(""" insert into user_data(username,password,profile_name) values(%s,%s,%s);""",(username,hash_password,p_name))
        db_connect.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@n.route("/signin",methods=["GET","POST"])
def login():
    if "username" in session :
        return redirect(url_for("dashboard"))

    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        cursr.execute("""select username,password from user_data where username=%s;""",(username,))
        data=cursr.fetchone()

        if not data:
            return render_template("register.html",info="user not registered plz register first")
        
        if username==data[0] and check_password_hash(data[1],password):
            session["username"]=username
            return redirect(url_for("dashboard"))
        
        else:
            return render_template("login.html",info="wrong password ")


    return render_template("login.html")


@n.route("/dashboard",methods=["GET","POST"])
@n.route("/dashboard/<title>/<mode>",methods=["GET","POST"])
def dashboard(title=None,mode=None):
    if "username" not in session:
        return redirect(url_for("login"))
    
    username=session.get("username")
    cursr.execute("select profile_name from user_data where username=%s;",(username,))
    data=cursr.fetchone()

    cursr.execute("""select title from  notes where username=%s;""",(username,))
    data1=cursr.fetchall() #[(t1,),(t2,),(t3,),(t4,)]
    
    notes_info=" "
    c_mode=""

    if mode=="read":
         cursr.execute(""" select notes from notes where username=%s and title = %s;""",(username,title))
         notes_info=cursr.fetchone() #(notes,)
         c_mode="read"

    elif mode=="update":
         cursr.execute(""" select notes from notes where username=%s and title = %s;""",(username,title))
         notes_info=cursr.fetchone() #(notes,)
         c_mode="update"
    
    elif mode=="delete":
        cursr.execute(""" delete from  notes where username=%s and title = %s;""",(username,title))
        db_connect.commit()

        return redirect(url_for("dashboard"))

   
    if data:
      return render_template("dashboard.html",profile_name=data[0],notes=data1,s_mode=c_mode,notes_info= notes_info[0],title=title)
    
    
@n.route("/notes_form", methods=["GET","POST"])   
def notes_form():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username=session.get("username")
    if request.method=="POST":
        title=request.form["title"]
        notes=request.form["notes"]
        cursr.execute("""select title from notes where username=%s;""",(username,))
        data=cursr.fetchall()   #  (t1,) in [(t1),(t2),(t3)]

        if (title,) in data:
            return render_template("notes_form.html",re_notes=notes,info="title already exists plz use another",re_title=title)
        
        cursr.execute("insert into notes (username,title,notes) values(%s,%s,%s);",(username,title,notes))
        db_connect.commit()
        return  redirect(url_for("dashboard"))

    return render_template("notes_form.html")

@n.route("/update_notes",methods=["GET","POST"])
def update_notes():

    if "username" not in session:
        return redirect(url_for("login"))
    
    username=session.get("username")
    if request.method=="POST":
        title=request.form["title"]
        u_notes=request.form["notes_update"]

        cursr.execute(""" update notes set notes=%s where username=%s and title=%s;""",(u_notes,username,title))
        db_connect.commit()
        return redirect(url_for("dashboard"))

@n.route("/logout")
def logout():
   if "username" not in session:
       return redirect(url_for("login"))
   
   session.clear()
   return redirect(url_for("welcome"))

if __name__=="__main__":
    n.run(debug=True)