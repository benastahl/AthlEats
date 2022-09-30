from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return redirect("/signup", 302)


@app.route("/login", methods=["GET"])
def display_login():
    return render_template("login.html")


@app.route("/signup", methods=["GET"])
def display_signup():
    return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def process_signup():
    try:
        tos_agree = request.form["tos-agree"]
        email = request.form["email"]
        password = request.form["pass"]
    except:
        return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)
