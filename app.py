from flask import Flask,render_template,request,session,redirect
from DB import Database
import requests
import json
import genai

app=Flask(__name__)
app.secret_key = 'mera_naam_gopal'

dbo=Database()

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/registration")
def register():
    return render_template("registration.html")

@app.route("/perform_registration",methods=["post"])
def perform_reg():
    name=request.form.get("user_name")
    email=request.form.get("user_mail")
    mobile=request.form.get("user_mobile")
    password=request.form.get("user_pass")

    response=dbo.import_data(email,mobile,name,password)

    if(response):
        message="Succesfully Registered"
        return render_template("login.html",message=message)
    else:
        message="User Already Exist"
        return render_template("registration.html",message=message)
    
@app.route('/perform_login',methods=['post'])
def perform_login():
    email=request.form.get("user_mail")
    password=request.form.get("user_pass")

    response=dbo.check(email,password)

    if(response):
        session['logged_in']=True
        return redirect("/home")
    else:
        message="Incorrect Credentials"
        return render_template("login.html",message=message)
    
@app.route("/home")
def home():
    if 'logged_in' in session and session['logged_in'] :
        return render_template("home.html")
    else:
        return redirect("/")
    
@app.route("/model",methods=['post'])
def model():
    if 'logged_in' in session and session['logged_in'] :
        response=request.form.get("output")

        if(response=="Sentiment Analysis"):
            return render_template('model.html',response=response)
        elif(response=="Emotion Detection"):
            return render_template('model.html',response=response)
        elif(response=="NER"):
            return render_template('model.html',response=response)
        elif(response=="Recipe Recommendation"):
            return render_template('model.html',response=response)
        elif(response=="LOGOUT"):
            return redirect('/logout')
    else:
        return redirect("/")
    
@app.route('/model/recipe',methods=['post'])
def recipe():
    if 'logged_in' in session and session['logged_in'] :
        input=request.form.get("input_text")
        response=requests.get("http://127.0.0.1:6000/api/recipe?{}".format(input))
        response_str = response.content.decode("utf-8")
        response=json.loads(response_str)
        return render_template('model.html',response="Recipe Recommendation",output=response)
    else:
        return redirect("/")
    
@app.route('/model/sentiment',methods=['post'])
def sentiment():
    if 'logged_in' in session and session['logged_in'] :
        text=request.form.get("input_text")
        result=genai.sentiment_check(text)
        return render_template('model.html',response="Sentiment Analysis",output=result)
    else:
        return redirect("/")
    
@app.route('/model/emotion',methods=['post'])
def emotion():
    if 'logged_in' in session and session['logged_in'] :
        text=request.form.get("input_text")
        result=genai.emotion_check(text)
        return render_template('model.html',response="Emotion Detection",output=result)
    else:
        return redirect("/")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


app.run(debug=True)