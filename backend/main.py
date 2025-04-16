from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

players = [
    {"id": 1, "name": "Marco Bianchi"},
    {"id": 2, "name": "Giulia Rossi"},
    {"id": 3, "name": "Lorenzo Verdi"},
    {"id": 4, "name": "Sara Neri"},
    {"id": 5, "name": "Matteo Gallo"},
    {"id": 6, "name": "Elena Fontana"},
    {"id": 7, "name": "Davide Rinaldi"},
    {"id": 8, "name": "Chiara Conti"},
]

conn = sqlite3.connect("votes.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS votes (player_id INTEGER, ip TEXT, timestamp TEXT)")

class Vote(BaseModel):
    player_id: int

@app.get("/players")
def get_players():
    return players

@app.post("/vote")
def vote(vote: Vote, request: Request):
    deadline = datetime(2025, 4, 20, 23, 59)
    if datetime.now() > deadline:
        return {"error": "Votazione chiusa"}
    ip = request.client.host
    cur = conn.execute("SELECT * FROM votes WHERE ip = ?", (ip,))
    if cur.fetchone():
        return {"error": "Hai già votato"}
    conn.execute("INSERT INTO votes (player_id, ip, timestamp) VALUES (?, ?, ?)", (vote.player_id, ip, datetime.now().isoformat()))
    conn.commit()
    return {"message": "Voto registrato"}

@app.get("/results")
def results():
    cur = conn.execute("SELECT player_id, COUNT(*) FROM votes GROUP BY player_id")
    return [{"player_id": row[0], "votes": row[1]} for row in cur.fetchall()]
