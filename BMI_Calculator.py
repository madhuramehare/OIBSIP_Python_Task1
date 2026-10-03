
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
DB_NAME = "bmi_database.db"
def create_database():
    """Create the database and BMI table if they don't exist."""
    try:
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not create database:\n{error}"
        )

def calculate_bmi():
    """Calculate BMI and save the record."""

    name = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()
    if not name:
        messagebox.showwarning(
            "Input Error",
            "Please enter the user's name."
        )
        return

    if not weight_text or not height_text:
        messagebox.showwarning(
            "Input Error",
            "Please enter both weight and height."
        )
        return

    try:
        weight = float(weight_text)
        height = float(height_text)

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Weight and height must be numbers."
        )
        return

    if weight <= 0:
        messagebox.showwarning(
            "Invalid Weight",
            "Weight must be greater than 0."
        )
        return

    if height <= 0:
        messagebox.showwarning(
            "Invalid Height",
            "Height must be greater than 0."
        )
        return

    bmi = weight / (height * height)

    if bmi < 18.5:
        category = "Underweight"
        result_label.config(fg="orange")

    elif bmi < 25:
        category = "Normal"
        result_label.config(fg="green")

    elif bmi < 30:
        category = "Overweight"
        result_label.config(fg="orange")

    else:
        category = "Obese"
        result_label.config(fg="red")

    result_label.config(
        text=f"BMI: {bmi:.2f}\nCategory: {category}"
    )
    try:
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            weight,
            height,
            bmi,
            category,
            current_date
        ))

        connection.commit()
        connection.close()

        messagebox.showinfo(
            "Success",
            "BMI calculated and record saved successfully!"
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not save the record:\n{error}"
        )

def show_history():
    """Display saved BMI records for the selected user."""

    name = name_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Input Error",
            "Please enter a user's name first."
        )
        return

    try:
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT weight, height, bmi, category, date
            FROM bmi_records
            WHERE name = ?
            ORDER BY date ASC
        """, (name,))

        records = cursor.fetchall()
        connection.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not read database:\n{error}"
        )
        return

    if not records:
        messagebox.showinfo(
            "No Records",
            f"No BMI records found for {name}."
        )
        return

    history_window = tk.Toplevel(root)
    history_window.title(f"BMI History - {name}")
    history_window.geometry("750x400")

    title = tk.Label(
        history_window,
        text=f"BMI History of {name}",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=10)

    columns = (
        "Weight",
        "Height",
        "BMI",
        "Category",
        "Date"
    )

    table = ttk.Treeview(
        history_window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=130)

    for record in records:
        table.insert("", tk.END, values=record)

    table.pack(
        fill=tk.BOTH,
        expand=True,
        padx=10,
        pady=10
    )

def show_graph():
    """Display BMI trend graph for a user."""

    name = name_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Input Error",
            "Please enter a user's name first."
        )
        return

    try:
        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT bmi, date
            FROM bmi_records
            WHERE name = ?
            ORDER BY date ASC
        """, (name,))

        records = cursor.fetchall()
        connection.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Could not read database:\n{error}"
        )
        return

    if not records:
        messagebox.showinfo(
            "No Records",
            f"No BMI records found for {name}."
        )
        return

    bmi_values = [record[0] for record in records]
    dates = [record[1] for record in records]

    # Create graph
    plt.figure(figsize=(9, 5))

    plt.plot(
        dates,
        bmi_values,
        marker="o",
        linewidth=2
    )

    plt.axhline(
        y=18.5,
        linestyle="--",
        label="Underweight limit"
    )

    plt.axhline(
        y=24.9,
        linestyle="--",
        label="Normal upper limit"
    )

    plt.axhline(
        y=29.9,
        linestyle="--",
        label="Overweight upper limit"
    )

    plt.title(f"BMI Trend - {name}")
    plt.xlabel("Date")
    plt.ylabel("BMI")

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def clear_fields():
    name_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)

    result_label.config(
        text="BMI: --\nCategory: --",
        fg="black"
    )

create_database()

root = tk.Tk()

root.title("BMI Calculator")
root.geometry("550x600")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 26, "bold")
)

title_label.pack(pady=20)


subtitle_label = tk.Label(
    root,
    text="Calculate and track your Body Mass Index",
    font=("Arial", 11)
)

subtitle_label.pack(pady=5)

frame = tk.Frame(root)
frame.pack(pady=20)

name_label = tk.Label(
    frame,
    text="User Name:",
    font=("Arial", 12)
)

name_label.grid(
    row=0,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

name_entry = tk.Entry(
    frame,
    width=25,
    font=("Arial", 12)
)

name_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=10
)

weight_label = tk.Label(
    frame,
    text="Weight (kg):",
    font=("Arial", 12)
)

weight_label.grid(
    row=1,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

weight_entry = tk.Entry(
    frame,
    width=25,
    font=("Arial", 12)
)

weight_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=10
)

height_label = tk.Label(
    frame,
    text="Height (meters):",
    font=("Arial", 12)
)

height_label.grid(
    row=2,
    column=0,
    padx=10,
    pady=10,
    sticky="w"
)

height_entry = tk.Entry(
    frame,
    width=25,
    font=("Arial", 12)
)

height_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=10
)
calculate_button = tk.Button(
    root,
    text="Calculate BMI",
    font=("Arial", 12, "bold"),
    command=calculate_bmi,
    width=20
)

calculate_button.pack(pady=10)
result_label = tk.Label(
    root,
    text="BMI: --\nCategory: --",
    font=("Arial", 18, "bold"),
    fg="black"
)

result_label.pack(pady=20)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

history_button = tk.Button(
    button_frame,
    text="View History",
    font=("Arial", 11),
    command=show_history,
    width=15
)

history_button.grid(
    row=0,
    column=0,
    padx=5
)

graph_button = tk.Button(
    button_frame,
    text="BMI Trend",
    font=("Arial", 11),
    command=show_graph,
    width=15
)

graph_button.grid(
    row=0,
    column=1,
    padx=5
)

clear_button = tk.Button(
    button_frame,
    text="Clear",
    font=("Arial", 11),
    command=clear_fields,
    width=15
)

clear_button.grid(
    row=1,
    column=0,
    columnspan=2,
    pady=10
)

info_label = tk.Label(
    root,
    text=(
        "BMI Categories:\n"
        "Below 18.5  → Underweight\n"
        "18.5 - 24.9 → Normal\n"
        "25 - 29.9   → Overweight\n"
        "30+         → Obese"
    ),
    font=("Arial", 10),
    justify="left"
)

info_label.pack(pady=15)

root.mainloop()
