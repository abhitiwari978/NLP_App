from flask import Flask,render_template,request,jsonify
import models

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/api/recipe")
def recipe():
    text=str(request.args.get('user_text'))
    data=models.recommend_recipes_api(text)
    return jsonify(data)

app.run(debug=True,port=6000)