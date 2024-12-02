from flask import (
    Flask,
    request,
    send_file,
    render_template_string,
    redirect,
    url_for,
)
import sqlite3
import os
import mimetypes

app = Flask(__name__)

DATA_FOLDER = "./data"
DB_FILE = "./files.db"

# Create the database if it doesn't exist
if not os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE files (filename TEXT PRIMARY KEY, password TEXT)"""
    )
    conn.commit()
    conn.close()


@app.route("/secured_drive/", methods=["GET", "POST"])
def secured_drive():
    filename = request.args.get("filename")
    password = request.args.get(
        "passwd"
    )  # Check if password is in the query parameters

    if not filename:
        return "Filename not provided", 400

    # If both filename and password are provided as query parameters
    if password:
        # Check the database for the filename and password
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT 1 FROM files WHERE filename = ? AND password = ?",
            (filename, password),
        )
        result = c.fetchone()
        conn.close()

        if result:
            file_path = os.path.join(DATA_FOLDER, filename)
            if os.path.exists(file_path):
                # Detect MIME type
                mime_type, _ = mimetypes.guess_type(file_path)
                return send_file(file_path, mimetype=mime_type)
            else:
                return "File not found", 404
        else:
            return render_template_string(
                """
                <!doctype html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                </head>
                <body>
                    <div class="container">
                        <h1>Access Denied</h1>
                        <p>Invalid filename or password.</p>
                        <a href="/secured_drive?filename={{ filename }}">Try again</a>
                    </div>
                </body>
                </html>
                """,
                filename=filename,
            )

    # If only filename is provided, display the password form
    if request.method == "POST":
        password = request.form.get("password")
        if not password:
            return "Password not provided", 400

        # Redirect with both filename and password in the query parameters
        return redirect(
            url_for("secured_drive", filename=filename, passwd=password)
        )

    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <div class="container">
                <h1>Enter Password for {{ filename }}</h1>
                <form method="post">
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Submit</button>
                </form>
            </div>
        </body>
        </html>
        """,
        filename=filename,
    )


if __name__ == "__main__":
    # Ensure the data folder exists
    os.makedirs(DATA_FOLDER, exist_ok=True)
    app.run(debug=True)
