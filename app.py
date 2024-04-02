from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import pandas as pd
import numpy as np
import sklearn
import warnings
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn import svm
from sklearn.model_selection import train_test_split
from joblib import load

warnings.filterwarnings('ignore')

app = Flask(__name__)

input_dict ={}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/farmer_signup', methods=['GET','POST'])
def farmer_signup():
    if request.method == 'GET':
        return render_template('farmer_signup.html')
    elif request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        location = request.form.get('location')

        db_file = "crop_yield.db"

        try:
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
        except sqlite3.Error as e:
            print("Error connecting to database:", e)
            exit()

        query = "CREATE TABLE IF NOT EXISTS farmers(name TEXT, email TEXT PRIMARY KEY, password TEXT , phone TEXT, location TEXT)"
        try:
            cur.execute(query)
        except sqlite3.Error as e:
            print("Error executing query:", e)
            conn.close()
            exit()

        query = "INSERT INTO farmers VALUES(?,?,?,?,?)"
        try:
            input_dict["yield"] = 0
            cur.execute(query, (name, email, password, phone, location))
            conn.commit()  # Add this line to commit the changes to the database
            return redirect(url_for('farmer_login'))
        
        except sqlite3.Error as e:
            print("Error executing query:", e)
            conn.close()
            return render_template('farmer_signup.html',error="Email alredy registered")
        # return redirect(url_for('farmer_login'))

@app.route('/predict', methods=['POST'])
def predict():
    email=request.form.get('email')
    return render_template('predict.html',email=email)


@app.route('/farmer_login')
def farmer_login():
    db_file = "crop_yield.db"

    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        exit()
    query = "CREATE TABLE IF NOT EXISTS farmers(name TEXT, email TEXT PRIMARY KEY, password TEXT , phone TEXT, location TEXT)"
    try:
        cur.execute(query)
    except sqlite3.Error as e:
        print("Error executing query:", e)
        conn.close()
        exit()
    return render_template('farmer_login.html')

@app.route('/farmer_dashboard', methods=['POST'])
def farmer_dashboard():
    email = request.form.get('email')
    password = request.form.get('password')
    db_file = "crop_yield.db"
    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        exit()
    query = "SELECT * FROM farmers WHERE email = ?"
    try:
        cur.execute(query, (email,))
        rows = cur.fetchall()
        if len(rows) == 0:
            # Email does not exist in the database
            return render_template('farmer_login.html', error="Email does not exist")
        else:
            # Email exists, check password
            stored_password = rows[0][2]  # Assuming password is stored in the third column
            if password == stored_password:
                name= rows[0][0]
                # Password is correct, log in the farmer
                
                query = "SELECT * FROM data WHERE email = ?"
                try:
                    cur.execute(query, (email,))
                    rows = cur.fetchall()
                except:
                    rows = []
                    
                return render_template('farmer_dashboard.html',name=name, email=email, logged_in=True, rows=rows)
            else:
                # Password is incorrect
                return render_template('farmer_login.html', error="Incorrect password")
    except sqlite3.Error as e:
        print("Error executing query:", e)
        conn.close()
        exit()



@app.route('/output', methods=['POST'])
def output():
    email = request.form.get('email')
    input_dict["rainfall"] = request.form.get('rainfall')
    input_dict["fertilizer"] = request.form.get('fertilizer')
    input_dict["temperature"] = request.form.get('temperature')
    input_dict["nitrogen"] = request.form.get('nitrogen')
    input_dict["phosphorus"] = request.form.get('phosphorus')
    input_dict["potassium"] = request.form.get('potassium')

    svm = load('SVM_model.joblib')

    # Make predictions for a single data point
    input_data = np.array([[float(input_dict['rainfall']), float(input_dict['fertilizer']), float(input_dict['temperature']), float(input_dict['nitrogen']), float(input_dict['phosphorus']), float(input_dict['potassium'])]])
    prediction = svm.predict(input_data)
    print("Predicted Yield:", prediction[0])


    db_file = "crop_yield.db"

    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        exit()

    query = "CREATE TABLE IF NOT EXISTS data(email TEXT , rainfall int, fertilizer int, temperature int, nitrogen int, phosphorus int, potassium int, yield int)"
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print("Error executing query:", e)
        conn.close()
        exit()

    query = "INSERT INTO data VALUES(?,?,?,?,?,?,?,?)"
    try:
        cur.execute(query, (email, input_dict["rainfall"], input_dict["fertilizer"], input_dict["temperature"], input_dict["nitrogen"], input_dict["phosphorus"], input_dict["potassium"], prediction[0]))
        conn.commit()  # Add this line to commit the changes to the database
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print("Error executing query:", e)
        conn.close()
        exit()

    return render_template('output.html', data=input_dict, prediction=prediction[0])



@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'GET':
        return render_template('admin.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == "admin" and password == "admin":
            db_file = "crop_yield.db"
            try:
                conn = sqlite3.connect(db_file)
                cur = conn.cursor()
            except sqlite3.Error as e:
                print("Error connecting to database:", e)
                exit()
            query1 = "CREATE TABLE IF NOT EXISTS data(email TEXT , rainfall int, fertilizer int, temperature int, nitrogen int, phosphorus int, potassium int, yield int)"
            query2 = "SELECT * FROM data"
            qurey3 = "SELECT rainfall FROM data order by rainfall"
            query4 = "SELECT yield from data order by rainfall "
            query5 = "SELECT fertilizer from data order by fertilizer"
            query6 = "SELECT yield from data order by fertilizer"
            query7 = "SELECT temperature from data order by temperature"
            query8 = "SELECT yield from data order by temperature"
            query9 = "SELECT nitrogen from data order by nitrogen"
            query10 = "SELECT yield from data order by nitrogen"
            query11 = "SELECT phosphorus from data order by phosphorus"
            query12 = "SELECT yield from data order by phosphorus"
            query13 = "SELECT potassium from data order by potassium"
            query14 = "SELECT yield from data order by potassium"
            try:
                cur.execute(query1)
                cur.execute(query2)
                rows = cur.fetchall()
                cur.execute(qurey3)
                rfl = cur.fetchall()
                rainfall_values = [row[0] for row in rfl]
                cur.execute(query4)
                yld_rain = cur.fetchall()
                yield_values_rain = [row[0] for row in yld_rain]
                cur.execute(query5)
                fertilizer_values = cur.fetchall()
                cur.execute(query6)
                yld_fertilizer = cur.fetchall()
                yield_values_fertilizer = [row[0] for row in yld_fertilizer]
                cur.execute(query7)
                temperature_values = cur.fetchall()
                cur.execute(query8)
                yld_temperature = cur.fetchall()
                yield_values_temperature = [row[0] for row in yld_temperature]
                cur.execute(query9)
                nitrogen_values = cur.fetchall()
                cur.execute(query10)
                yld_nitrogen = cur.fetchall()
                yield_values_nitrogen = [row[0] for row in yld_nitrogen]
                cur.execute(query11)
                phosphorous_values = cur.fetchall()
                cur.execute(query12)
                yld_phosphorus = cur.fetchall()
                yield_values_phosphorous = [row[0] for row in yld_phosphorus]
                cur.execute(query13)
                potassium_values = cur.fetchall()
                cur.execute(query14)
                yld_potassium = cur.fetchall()
                yield_values_potassium = [row[0] for row in yld_potassium]
                return render_template('admin.html', rows=rows, rainfall_values=rainfall_values,fertilizer_values=fertilizer_values, temperature_values =temperature_values,nitrogen_values = nitrogen_values, phosphorous_values= phosphorous_values, potassium_values= potassium_values, yield_values_rain=yield_values_rain ,yield_values_fertilizer= yield_values_fertilizer,yield_values_temperature = yield_values_temperature,yield_values_nitrogen= yield_values_nitrogen, yield_values_potassium= yield_values_potassium, yield_values_phosphorous=yield_values_phosphorous, is_logged_in=True)
            except sqlite3.Error as e:
                print("Error executing query:", e)
                conn.close()
                exit()
        else:
            return render_template('admin.html', error="Invalid credentials")
    return render_template('admin.html')

# Load your dataset
# Assuming your dataset is in a CSV file named 'data.csv'

if __name__ == '__main__':
    app.run(debug=True)










































