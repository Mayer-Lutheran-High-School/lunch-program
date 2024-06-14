from flask import Flask, render_template, send_file, render_template_string, redirect
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy
import csv
from datetime import date, datetime
import webbrowser
import os




today = date.today()
#webbrowser.open('http://127.0.0.1:5005')

app = Flask(__name__)
socketio = SocketIO(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

filename = str(today) + ".csv"

    # writing the fields

entree_price = 2.00
side_price = 1.00
milk_price = 0.50
drink_price = 2.50
snack_price = 1.50

active = []
active_total = 0
active_student = "No Student Selected"
active_path = ""
active_grade = '0'

class Students(db.Model):
    __tablename__ = 'Students'
    id = db.Column(db.Integer, primary_key=True)
    card_num = db.Column(db.Integer, nullable=False)
    First_Name = db.Column(db.String(100), nullable=False)
    Last_Name = db.Column(db.String(20), nullable=True)
    Search_code = db.Column(db.String(20), nullable=True)
    Grade = db.Column(db.Integer, nullable=True)
    img = db.Column(db.String(20), nullable=True)







@app.route('/')
def home():
    return render_template('beta.html')


@app.route('/list')
def list():
    return render_template('list.html')


@app.route('/update_image/<path:image_path>')
def update_image(image_path):
    # Check if the image exists
    if os.path.exists(image_path):
        # Return the image
        return send_file(image_path, mimetype='image/png')
    else:
        return "Image not found", 404



@app.route('/lookup/<path:card>')
def lookup(card):
    global active_student
    global active_total
    global active_path
    global active_grade
    c = Students.query.filter_by(card_num=card).first()
    active_student = c.First_Name + " " + c.Last_Name
    active_path = c.img
    active_grade = str(c.Grade)
    return redirect("http://127.0.0.1:5005/")



@socketio.on('list')
def list(msg):
    new_page("http://127.0.0.1:5005/list")



def new_page(page):
    emit('new_page',  page, broadcast=True)


@socketio.on('dropdownlist')
def dropdownlist(msg):
    global active_grade
    html = ""

    print('drop-list: ' + str(msg))
    active_grade = msg["data"]
    if (msg["data"] != "0"):
        current = Students.query.order_by(Students.First_Name).filter_by(Grade=active_grade).all()
        for stu in current:
            #html = html + "<img href=\"/search/" + str(stu.card_num) + "\" src=/update_image/" + str(stu.img) + " style=\"width: 200px; height: auto;\">" + "\n" + "<p>" + stu.First_Name + " " + stu.Last_Name + "<p>" + "\n"
            print(stu.img)
            html = html + "<button style=\"width: 300px; height: 300px; background: url(" + "/update_image/" + stu.img + "); background-size: cover;\" class=\"image-button\" onclick=\"window.location.href=\'" + "http://127.0.0.1:5005/lookup/" + str(stu.card_num) + "\'\"></button>" + "\n" + "<p>" + stu.First_Name + " " + stu.Last_Name + "<p>" + "\n"

        emit('droptext', msg["data"] + "th grade", broadcast=True)
        print(html)

        emit('update_html',html, broadcast=True)
    else:
        current = Students.query.order_by(Students.First_Name).all()
        for stu in current:
            #html = html + "<img href=\"/search/" + str(stu.card_num) + "\" src=/update_image/" + str(stu.img) + " style=\"width: 200px; height: auto;\">" + "\n" + "<p>" + stu.First_Name + " " + stu.Last_Name + "<p>" + "\n"
            print(stu.img)
            html = html + "<button style=\"width: 300px; height: 300px; background: url(" + "/update_image/" + stu.img + "); background-size: cover;\" class=\"image-button\" onclick=\"window.location.href=\'" + "http://127.0.0.1:5005/lookup/" + str(stu.card_num) + "\'\"></button>" + "\n" + "<p>" + stu.First_Name + " " + stu.Last_Name + "<p>" + "\n"

        emit('droptext',  "Grade (Optional) ", broadcast=True)
        print(html)

        emit('update_html', html, broadcast=True)




@socketio.on('dropdown')
def dropdown(msg):
    global active_grade
    print('drop: ' + str(msg))
    active_grade = msg["data"]
    if (msg["data"] != "0"):
        emit('droptext', msg["data"] + "th grade", broadcast=True)
    else:

        emit('droptext',  "Grade (Optional) ", broadcast=True)



@socketio.on('message')
def handle_message(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)


@socketio.on('refresh')
def refresh(msg):
    ini()

@socketio.on('id')
def handle_message(msg):
    global active_student
    global active_path
    print('id: ' + str(msg["message"]))
    ms = str(msg["message"])
    existing_user = Students.query.filter_by(card_num=ms).first()
    if existing_user:
        send(existing_user.First_Name + " " + existing_user.Last_Name, broadcast=True)
        active_student = existing_user.First_Name + " " + existing_user.Last_Name
        active_path = existing_user.img
        print(active_path)
        emit('img', active_path, broadcast=True)
    else:
        send("Not a registered student", broadcast=True)



@socketio.on('search')
def handle_message(msg):
    global active_student
    global active_path
    print('search: ' + str(msg["message"]))
    ms = str(msg["message"])
    existing_user = Students.query.filter_by(Search_code=ms).first()
    if (active_grade != "0"):
        existing_user = existing_user.query.filter_by(Grade=active_grade).filter_by(Search_code=ms).first()
   # print(existing_user.First_Name)

    if existing_user:

        send(existing_user.First_Name + " " + existing_user.Last_Name, broadcast=True)
        active_student = existing_user.First_Name + " " + existing_user.Last_Name
        active_path = existing_user.img
        emit('img', active_path, broadcast=True)
    else:
        send("Not a registered student", broadcast=True)
        active_path = "C:\\Users\\nyg4\PycharmProjects\pythonProject\images\default.png"
        emit('img', active_path, broadcast=True)


@socketio.on('funct')
def funct(msg):
    global active
    global active_student
    global active_total
    global active_path
    global active_grade
    if (msg["data"] == 'clear'):
        active = []
    elif (msg["data"] == 'complete'):

        if (active_student != "No Student Selected"):

                # creating a csv writer object

            # writing the fields
            with open(filename, 'a') as csvfile:
                # creating a csv writer object
                entry = ""

                flag = True

                for item in active:
                    if flag:
                        entry = entry + str(datetime.now()) + ", " + active_student + ", " + str(item)
                        flag = False
                    else:
                        entry = entry + ", " +  str(item) + "\n"
                        flag = True

                csvfile.write(entry)
            active = []
            active_student = "No Student Selected"
            active_total = "$0.00"
            active_path = "C:\\Users\\nyg4\PycharmProjects\pythonProject\images\default.png"
            active_grade = '0'

    ini()

@socketio.on('item')
def item(data):
    global active
    if (data["data"] == "entree"):
        active.append("entree")
        active.append(entree_price)
    elif (data["data"] == "side"):
        active.append("side")
        active.append(side_price)
    elif (data["data"] == "milk"):
        active.append("milk")
        active.append(milk_price)
    elif (data["data"] == "drink"):
        active.append("drink")
        active.append(drink_price)
    elif (data["data"] == "snack"):
        active.append("A la carte")
        active.append(snack_price)
    snd()


def ini():
    global active_total
    global active
    global active_student
    global active_path
    active_total = 0.0
    ms = ""
    flag = True
    for a in active:
        if flag:
            ms += a + ": $"
            flag = False
        else:
            ms += str(a) + "0\n"
            active_total = active_total + a
            flag = True
    emit('total', ms, broadcast=True)
    emit('sum', "$" + str(active_total) + "0", broadcast=True)
    emit('message', active_student, broadcast=True)
    if (active_grade != "0"):
        emit('droptext', str(active_grade) + "th grade", broadcast=True)
    else:
        emit('droptext',  "Grade (Optional) ", broadcast=True)
    emit('img', active_path, broadcast=True)
def snd():
    global active_total
    global active
    global active_student
    active_total = 0.0
    ms = ""
    flag = True
    for a in active:
        if flag:
            ms += a + ": $"
            flag = False
        else:
            ms += str(a) + "0\n"
            active_total = active_total + a
            flag = True
    emit('total', ms, broadcast=True)
    emit('sum', "$" + str(active_total) + "0", broadcast=True)
    emit('message', active_student, broadcast=True)


@socketio.on('custom_event')
def handle_custom_event(data):
    print('Button was pressed!')
    emit('total', "button_pressed\ntest", broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()


    socketio.run(app, host='0.0.0.0', port=5005, debug=True, allow_unsafe_werkzeug=True)

