import typer
from typing import List, Optional
import sqlite3
from rich.console import Console
from rich.table import Table
from datetime import datetime

app = typer.Typer()
console = Console()

# Database setup
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
''')

conn.commit()

class Task:
    def __init__(self, id: int, description: str, status: str, created_at: str, updated_at: str):
        self.id = id
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return f"Task(id={self.id}, description={self.description}, status={self.status}, created_at={self.created_at}, updated_at={self.updated_at})"

@app.command()
def add(description: str):
    now = datetime.now().isoformat()
    c.execute('INSERT INTO tasks (description, status, created_at, updated_at) VALUES (?, ?, ?, ?)', (description, 'todo', now, now))
    conn.commit()
    console.print("[green]Task added successfully[/green]")

@app.command()
def update(task_id: int, description: str):
    now = datetime.now().isoformat()
    c.execute('UPDATE tasks SET description = ?, updated_at = ? WHERE id = ?', (description, now, task_id))
    conn.commit()
    if c.rowcount == 0:
        console.print(f"[red]Task {task_id} not found[/red]")
    else:
        console.print(f"[green]Task {task_id} updated successfully[/green]")

@app.command()
def delete(task_id: int):
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    if c.rowcount == 0:
        console.print(f"[red]Task {task_id} not found[/red]")
    else:
        console.print(f"[green]Task {task_id} deleted successfully[/green]")

@app.command(name="mark-in-progress")
def mark_in_progress(task_id: int):
    now = datetime.now().isoformat()
    c.execute('UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?', ('in-progress', now, task_id))
    conn.commit()
    if c.rowcount == 0:
        console.print(f"[red]Task {task_id} not found[/red]")
    else:
        console.print(f"[green]Task {task_id} marked as in-progress[/green]")

@app.command(name="mark-done")
def mark_done(task_id: int):
    now = datetime.now().isoformat()
    c.execute('UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?', ('done', now, task_id))
    conn.commit()
    if c.rowcount == 0:
        console.print(f"[red]Task {task_id} not found[/red]")
    else:
        console.print(f"[green]Task {task_id} marked as done[/green]")

@app.command()
def list(status: Optional[str] = typer.Argument(None)):
    if status:
        c.execute('SELECT id, description, status, created_at, updated_at FROM tasks WHERE status = ?', (status,))
    else:
        c.execute('SELECT id, description, status, created_at, updated_at FROM tasks')
    
    tasks = c.fetchall()
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
    else:
        table = Table(title="Tasks")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Created At", style="blue")
        table.add_column("Updated At", style="blue")

        for task in tasks:
            table.add_row(str(task[0]), task[1], task[2], task[3], task[4])

        console.print(table)

if __name__ == "__main__":
    app()
    conn.close()
