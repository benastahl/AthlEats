from flask import Flask, render_template

app = Flask(__name__)


@app.route("/login", methods=["GET"])
def display_login():
    return render_template("login.html")


@app.route("/signup", methods=["GET"])
def display_signup():
    return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)
