from flask import Flask, request, render_template, redirect, url_for
import requests
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
            conn.commit()  
            return redirect(url_for('farmer_login'))
        
        except sqlite3.Error as e:
            print("Error executing query:", e)
            conn.close()
            return render_template('farmer_signup.html',error="Email alredy registered")
        

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
            
            return render_template('farmer_login.html', error="Email does not exist")
        else:
            
            stored_password = rows[0][2]  
            if password == stored_password:
                name= rows[0][0]
                
                
                query = "SELECT * FROM data WHERE email = ?"
                try:
                    cur.execute(query, (email,))
                    rows = cur.fetchall()
                except:
                    rows = []
                    
                return render_template('farmer_dashboard.html',name=name, email=email, logged_in=True, rows=rows)
            else:
                
                return render_template('farmer_login.html', error="Incorrect password")
    except sqlite3.Error as e:
        print("Error executing query:", e)
        conn.close()
        exit()



@app.route('/output', methods=['POST'])
def output():
    email = request.form.get('email')
    api_data = fetchTmpAndRain(email)
    input_dict["temperature"] = api_data[0]
    input_dict["rainfall"] = api_data[1]
    # input_dict["rainfall"] = request.form.get('rainfall')
    input_dict["fertilizer"] = request.form.get('fertilizer')
    # input_dict["temperature"] = request.form.get('temperature')
    input_dict["nitrogen"] = request.form.get('nitrogen')
    input_dict["phosphorus"] = request.form.get('phosphorus')
    input_dict["potassium"] = request.form.get('potassium')

    svm = load('SVM_model.joblib')

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
        conn.commit()
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
            return render_template('admin.html', is_logged_in=True)
            # db_file = "crop_yield.db"
            # try:
            #     conn = sqlite3.connect(db_file)
            #     cur = conn.cursor()
            # except sqlite3.Error as e:
            #     print("Error connecting to database:", e)
            #     exit()
            # query1 = "CREATE TABLE IF NOT EXISTS data(email TEXT , rainfall int, fertilizer int, temperature int, nitrogen int, phosphorus int, potassium int, yield int)"
            # query2 = "SELECT * FROM data"
            # qurey3 = "SELECT rainfall FROM data order by rainfall"
            # query4 = "SELECT yield from data order by rainfall "
            # query5 = "SELECT fertilizer from data order by fertilizer"
            # query6 = "SELECT yield from data order by fertilizer"
            # query7 = "SELECT temperature from data order by temperature"
            # query8 = "SELECT yield from data order by temperature"
            # query9 = "SELECT nitrogen from data order by nitrogen"
            # query10 = "SELECT yield from data order by nitrogen"
            # query11 = "SELECT phosphorus from data order by phosphorus"
            # query12 = "SELECT yield from data order by phosphorus"
            # query13 = "SELECT potassium from data order by potassium"
            # query14 = "SELECT yield from data order by potassium"
            # try:
            #     cur.execute(query1)
            #     cur.execute(query2)
            #     rows = cur.fetchall()
            #     cur.execute(qurey3)
            #     rfl = cur.fetchall()
            #     rainfall_values = [row[0] for row in rfl]
            #     cur.execute(query4)
            #     yld_rain = cur.fetchall()
            #     yield_values_rain = [row[0] for row in yld_rain]
            #     cur.execute(query5)
            #     fertilizer_values = cur.fetchall()
            #     cur.execute(query6)
            #     yld_fertilizer = cur.fetchall()
            #     yield_values_fertilizer = [row[0] for row in yld_fertilizer]
            #     cur.execute(query7)
            #     temperature_values = cur.fetchall()
            #     cur.execute(query8)
            #     yld_temperature = cur.fetchall()
            #     yield_values_temperature = [row[0] for row in yld_temperature]
            #     cur.execute(query9)
            #     nitrogen_values = cur.fetchall()
            #     cur.execute(query10)
            #     yld_nitrogen = cur.fetchall()
            #     yield_values_nitrogen = [row[0] for row in yld_nitrogen]
            #     cur.execute(query11)
            #     phosphorous_values = cur.fetchall()
            #     cur.execute(query12)
            #     yld_phosphorus = cur.fetchall()
            #     yield_values_phosphorous = [row[0] for row in yld_phosphorus]
            #     cur.execute(query13)
            #     potassium_values = cur.fetchall()
            #     cur.execute(query14)
            #     yld_potassium = cur.fetchall()
            #     yield_values_potassium = [row[0] for row in yld_potassium]
            #     return render_template('admin.html', rows=rows, rainfall_values=rainfall_values,fertilizer_values=fertilizer_values, temperature_values =temperature_values,nitrogen_values = nitrogen_values, phosphorous_values= phosphorous_values, potassium_values= potassium_values, yield_values_rain=yield_values_rain ,yield_values_fertilizer= yield_values_fertilizer,yield_values_temperature = yield_values_temperature,yield_values_nitrogen= yield_values_nitrogen, yield_values_potassium= yield_values_potassium, yield_values_phosphorous=yield_values_phosphorous, is_logged_in=True)
            # except sqlite3.Error as e:
            #     print("Error executing query:", e)
            #     conn.close()
            #     exit()
    #     else:
    #         return render_template('admin.html', error="Invalid credentials")
    # return render_template('admin.html')



@app.route('/records')
def records():
    db_file = "crop_yield.db"
    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
        exit()
    query = "SELECT * FROM data"
    try:
        cur.execute(query)
        rows = cur.fetchall()
        return render_template('records.html', rows=rows)
    except sqlite3.Error as e:
        print("Error executing query:", e)
        conn.close()
        exit()

@app.route('/reports')
def reports():
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
        return render_template('reports.html', rows=rows, rainfall_values=rainfall_values,fertilizer_values=fertilizer_values, temperature_values =temperature_values,nitrogen_values = nitrogen_values, phosphorous_values= phosphorous_values, potassium_values= potassium_values, yield_values_rain=yield_values_rain ,yield_values_fertilizer= yield_values_fertilizer,yield_values_temperature = yield_values_temperature,yield_values_nitrogen= yield_values_nitrogen, yield_values_potassium= yield_values_potassium, yield_values_phosphorous=yield_values_phosphorous)
    except sqlite3.Error as e:
        print("Error executing query:", e)
        conn.close()
        exit()



def fetchTmpAndRain(email):
    con = sqlite3.connect('crop_yield.db')
    cur = con.cursor()
    query = "SELECT location FROM farmers WHERE email = ?"
    cur.execute(query, (email,))
    location = cur.fetchone()[0]


    if " " in location:
        firstname,secondname =location.split(" ")
        location = firstname + "%20" + secondname


    apikey= "HMY3LJFCPBTX77YGNHNBMKUU2"
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"+location+"/?key="+apikey

    try:
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            temperatures = []
            rainfalls = []
            for day in weather_data['days']:
                temperatures.append(day['temp'])
                rainfalls.append(day['precip'])

            average_temperature = sum(temperatures) / len(temperatures)
            average_rainfall = sum(rainfalls) / len(rainfalls)

            print("Average Temperature:", round(average_temperature, 2), "°F")
            print("Average Rainfall:", round(average_rainfall, 2), "inches")
            return (round(average_temperature, 2), round(average_rainfall, 2))

        else:
            print("Error:", response.status_code, response.text)
    except Exception as e:
        print("Error:", e)

@app.route('/algorithm')
def algorithm():
    return render_template('algorithm.html')


if __name__ == '__main__':
    app.run(debug=True)










































