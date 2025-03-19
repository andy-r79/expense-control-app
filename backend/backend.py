# Backend - FastAPI (Python)
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import date
from typing import List
import sqlite3

app = FastAPI()

# Baza danych - SQLite
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TEXT
)
""")
conn.commit()

# Model danych
class Expense(BaseModel):
    amount: float
    category: str
    description: str = ""
    date: str = date.today().isoformat()

# Endpoint do dodawania wydatku
@app.post("/expenses/")
def add_expense(expense: Expense):
    cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                   (expense.amount, expense.category, expense.description, expense.date))
    conn.commit()
    return {"message": "Expense added successfully"}

# Endpoint do pobierania wydatków
@app.get("/expenses/", response_model=List[Expense])
def get_expenses():
    cursor.execute("SELECT amount, category, description, date FROM expenses")
    expenses = cursor.fetchall()
    return [Expense(amount=row[0], category=row[1], description=row[2], date=row[3]) for row in expenses]

# Endpoint do sumowania wydatków
@app.get("/expenses/summary/")
def get_summary():
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0
    return {"total_spent": total}


# Prosty interfejs użytkownika
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Śledzenie Wydatków</title>
        <script>
            async function addExpense() {
                const amount = document.getElementById('amount').value;
                const category = document.getElementById('category').value;
                const description = document.getElementById('description').value;
                const date = document.getElementById('date').value;

                const response = await fetch('/expenses/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ amount, category, description, date })
                });
                if (response.ok) alert('Wydatek dodany!');
                else alert('Błąd dodawania wydatku');
            }
        </script>
    </head>
    <body>
        <h2>Dodaj wydatek</h2>
        <label>Kwota:</label><input type="number" id="amount"><br>
        <label>Kategoria:</label><input type="text" id="category"><br>
        <label>Opis:</label><input type="text" id="description"><br>
        <label>Data:</label><input type="date" id="date"><br>
        <button onclick="addExpense()">Dodaj</button>
    </body>
    </html>
    """

# Uruchomienie aplikacji: uvicorn filename:app --reload
