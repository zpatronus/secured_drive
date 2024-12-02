import sqlite3
import os
import argparse

DB_FILE = "./files.db"
DATA_FOLDER = "./data"


def connect_db():
    if not os.path.exists(DB_FILE):
        raise FileNotFoundError(
            f"Database file '{DB_FILE}' does not exist. Initialize it by running the Flask app first."
        )
    return sqlite3.connect(DB_FILE)


def add_file(filename, password):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO files (filename, password) VALUES (?, ?)",
            (filename, password),
        )
        conn.commit()
        print(f"File '{filename}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: File '{filename}' already exists in the database.")
    finally:
        conn.close()


def remove_file(filename):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM files WHERE filename = ?", (filename,))
    conn.commit()
    if c.rowcount > 0:
        print(f"File '{filename}' removed successfully.")
    else:
        print(f"Error: File '{filename}' not found in the database.")
    conn.close()


def modify_password(filename, new_password):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "UPDATE files SET password = ? WHERE filename = ?",
        (new_password, filename),
    )
    conn.commit()
    if c.rowcount > 0:
        print(f"Password for file '{filename}' updated successfully.")
    else:
        print(f"Error: File '{filename}' not found in the database.")
    conn.close()


def rename_file(old_filename, new_filename):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "UPDATE files SET filename = ? WHERE filename = ?",
        (new_filename, old_filename),
    )
    conn.commit()
    if c.rowcount > 0:
        old_path = os.path.join(DATA_FOLDER, old_filename)
        new_path = os.path.join(DATA_FOLDER, new_filename)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(
                f"File renamed from '{old_filename}' to '{new_filename}' successfully."
            )
        else:
            print(
                f"Database entry updated, but file '{old_filename}' not found in data folder."
            )
    else:
        print(f"Error: File '{old_filename}' not found in the database.")
    conn.close()


def list_files():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT filename, password FROM files")
    rows = c.fetchall()
    conn.close()
    if rows:
        print("Database contents:")
        for row in rows:
            print(f"  Filename: {row[0]}, Password: {row[1]}")
    else:
        print("Database is empty.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage the files database.")
    parser.add_argument(
        "action",
        choices=["add", "remove", "modify_password", "rename", "list"],
        help="Action to perform",
    )
    parser.add_argument("--filename", help="Filename to add, remove, or modify")
    parser.add_argument(
        "--password", help="Password for the file (add or modify_password)"
    )
    parser.add_argument("--new_filename", help="New filename for renaming")

    args = parser.parse_args()

    try:
        if args.action == "add":
            if args.filename and args.password:
                add_file(args.filename, args.password)
            else:
                print("Error: --filename and --password are required for 'add'")
        elif args.action == "remove":
            if args.filename:
                remove_file(args.filename)
            else:
                print("Error: --filename is required for 'remove'")
        elif args.action == "modify_password":
            if args.filename and args.password:
                modify_password(args.filename, args.password)
            else:
                print(
                    "Error: --filename and --password are required for 'modify_password'"
                )
        elif args.action == "rename":
            if args.filename and args.new_filename:
                rename_file(args.filename, args.new_filename)
            else:
                print(
                    "Error: --filename and --new_filename are required for 'rename'"
                )
        elif args.action == "list":
            list_files()
    except Exception as e:
        print(f"An error occurred: {e}")
