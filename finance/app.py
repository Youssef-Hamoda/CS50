import os
from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter to format currency
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Hook to run after every request to ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Homepage
@app.route("/")
@login_required
def index():
    # Retrieve user's portfolio and cash balance
    Stocks = db.execute(
        "SELECT * FROM portfolio WHERE user_id = ? GROUP BY stock", session["user_id"]
    )
    User = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # Calculate the total portfolio value
    portfolio_value = User[0]["cash"]
    for stock in Stocks:
        portfolio_value += stock["price"]

        # Calculate price per share and percent change
        stock["price_per"] = stock["price"] / stock["quantity"]
        current_price = lookup(stock["stock"])["price"]
        percent_change = (
            (current_price - float(stock["price_per"])) / float(stock["price_per"])
        ) * 100

        if percent_change >= 0:
            stock["percent_change"] = "+{:.2f}%".format(percent_change)
        else:
            stock["percent_change"] = "{:.2f}%".format(percent_change)

        stock["price"] = usd(stock["price"])
        stock["price_per"] = usd(stock["price_per"])

    portfolio_value = usd(portfolio_value)
    Cash = usd(User[0]["cash"])

    return render_template(
        "index.html", Cash=Cash, Stocks=Stocks, portfolio_value=portfolio_value
    )

# Buy stocks
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    User = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    Cash = User[0]["cash"]

    if request.method == "POST":
        symbol = request.form.get("symbol")

        shares = request.form.get("shares")
        if shares is None:
            return jsonify({"error": "Invalid quantity input"}), 400

        stock = lookup(symbol)
        if stock is None:
            return jsonify({"error": "Invalid stock symbol"}), 400

        try:
            shares = int(shares)
            if shares <= 0:
                raise ValueError("Invalid quantity input")
        except ValueError:
            return jsonify({"error": "Invalid quantity input"}), 400

        cost = stock["price"] * float(shares)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M")

        if int(cost) > Cash:
            return jsonify({"error": "Not enough funds"}), 400

        Cash -= cost

        # Update user's cash balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", Cash, session["user_id"])

        # Add the transaction to the transaction history
        db.execute(
            "INSERT INTO history (user_id, type, price, stock, quantity, time) VALUES(?, 'BUY', ?, ?, ?, ?)",
            session["user_id"],
            cost,
            symbol,
            int(shares),
            formatted_time,
        )

        # Check if the user already owns the stock
        result = db.execute(
            "SELECT COUNT(*) FROM portfolio WHERE user_id = ? AND stock = ?",
            session["user_id"],
            stock["symbol"],
        )
        if result[0]["COUNT(*)"] == 1:
            db.execute(
                "UPDATE portfolio SET quantity = quantity + ?, price = price + ? WHERE stock = ?",
                int(shares),
                cost,
                stock["symbol"],
            )
        else:
            db.execute(
                "INSERT INTO portfolio (user_id, stock, price, quantity) VALUES(?, ?, ?, ?)",
                session["user_id"],
                stock["symbol"],
                cost,
                int(shares),
            )

        new_entry = {
            "type": "BUY",
            "symbol": stock["symbol"],
            "price_per": usd(stock["price"]),
            "shares": shares,
            "price": usd(cost),
            "time": formatted_time,
            "cash": usd(Cash),
        }
        return jsonify(new_entry)
    else:
        History = db.execute(
            "SELECT * FROM history WHERE user_id = ? AND type = 'BUY' ORDER BY time DESC",
            session["user_id"],
        )

        for transaction in History:
            transaction["price_per"] = usd(
                transaction["price"] / transaction["quantity"]
            )
            transaction["price"] = usd(transaction["price"])

        return render_template("buy.html", History=History, Cash=usd(Cash))

# Transaction history
@app.route("/history")
@login_required
def history():
    History = db.execute(
        "SELECT * FROM history WHERE user_id = ? ORDER BY time DESC", session["user_id"]
    )

    User = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    Cash = User[0]["cash"]

    for transaction in History:
        transaction["price_per"] = usd(transaction["price"] / transaction["quantity"])
        transaction["price"] = usd(transaction["price"])

    return render_template("history.html", History=History, Cash=usd(Cash))

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide a username", "error")
            return render_template("login.html"), 400

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Please provide a password", "error")
            return render_template("login.html"), 400

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password", "error")
            return render_template("login.html"), 400

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Flash a success message
        flash("Login successful!", "success")

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")

# User logout
@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

# Get stock quote
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    User = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if request.method == "POST":
        symbol = request.form.get("symbol")

        stock = lookup(symbol)

        if stock is None:
            return jsonify({"error": "Invalid stock symbol"}), 400

        new_entry = {
            "symbol": stock["symbol"],
            "price": stock["price"],
        }
        return jsonify(new_entry)
    else:
        Cash = usd(User[0]["cash"])
        return render_template("quote.html", Cash=Cash)

# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # Check if username or password is blank
        if not username or not password or not confirm_password:
            flash("Please provide both username and password", "error")
            return render_template("register.html"), 400

        # Check if password and confirm_password match
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html"), 400

        # Check if password meets the requirements
        if (
            len(password) < 8
            or not any(char.isdigit() for char in password)
            or not any(char.isupper() for char in password)
            or not any(char in "!@#$%^&*()-_+=<>?/|\\{}[]" for char in password)
        ):
            flash("Password does not meet requirements", "error")
            return render_template("register.html"), 400

        # Check if username already exists
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            flash("Username is already taken", "error")
            return render_template("register.html"), 400

        # Generate password hash
        hashed_password = generate_password_hash(password)

        # Insert user into database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            hashed_password,
        )

        # Flash a success message
        flash("Registration successful. Please log in.", "success")

        # Redirect user to login page
        return redirect("/login")

    else:
        return render_template("register.html")

# Sell stocks
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    User = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    Cash = User[0]["cash"]

    if request.method == "POST":
        name = request.form.get("name")

        quantity = request.form.get("quantity")
        if quantity is None:
            return jsonify({"error": "Invalid quantity input"}), 400

        stock = lookup(name)
        if stock is None:
            return jsonify({"error": "Invalid stock symbol"}), 400

        result = db.execute(
            "SELECT COUNT(*) FROM portfolio WHERE user_id = ? AND stock = ?",
            session["user_id"],
            stock["symbol"],
        )
        if result[0]["COUNT(*)"] == 0:
            return jsonify({"error": "Stock not in possession"}), 400
        if int(quantity) <= 0:
            return jsonify({"error": "Invalid quantity input"}), 400

        cost = stock["price"] * float(quantity)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M")

        Cash += cost

        # Update user's cash balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", Cash, session["user_id"])

        # Add the transaction to the transaction history
        db.execute(
            "INSERT INTO history (user_id, type, price, stock, quantity, time) VALUES(?, 'SELL', ?, ?, ?, ?)",
            session["user_id"],
            cost,
            name,
            int(quantity),
            formatted_time,
        )
        db.execute(
            "UPDATE portfolio SET quantity = quantity - ?, price = price - ? WHERE stock = ?",
            int(quantity),
            cost,
            stock["symbol"],
        )

        new_entry = {
            "type": "SELL",
            "name": stock["symbol"],
            "price_per": usd(stock["price"]),
            "quantity": quantity,
            "price": usd(cost),
            "time": formatted_time,
            "cash": usd(Cash),
        }
        return jsonify(new_entry)
    else:
        History = db.execute(
            "SELECT * FROM history WHERE user_id = ? AND type = 'SELL' ORDER BY time DESC",
            session["user_id"],
        )

        for transaction in History:
            transaction["price_per"] = usd(
                transaction["price"] / transaction["quantity"]
            )
            transaction["price"] = usd(transaction["price"])

        return render_template("sell.html", History=History, Cash=usd(Cash))

# Add funds to the user's cash balance
@app.route("/funds", methods=["GET", "POST"])
@login_required
def funds():
    User = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    Cash = User[0]["cash"]

    if request.method == "POST":
        added_funds = request.form.get("funds")

        if int(added_funds) <= 0:
            return jsonify({"error": "Invalid quantity input"}), 400

        Cash += int(added_funds)

        # Update user's cash balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", Cash, session["user_id"])

        new_entry = {
            "cash": usd(Cash),
        }
        return jsonify(new_entry)
    else:
        return render_template("funds.html", Cash=usd(Cash))

if __name__ == "__main__":
    app.run()
