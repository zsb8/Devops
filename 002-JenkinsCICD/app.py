fromflaskimportFlask
app=Flask(__name__)

@app.route("/")
defhello():
return"HelloWorld!zsb2222222"

if__name__=="__main__":
app.run(host='0.0.0.0',port=8080)
