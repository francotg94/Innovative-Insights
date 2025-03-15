import json
import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime

# Function to load tasks from the JSON file
def load_tasks():
    if not os.path.exists("tasks.json"):
        return []
    try:
        with open("tasks.json", "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

# Function to save tasks to the JSON file
def save_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)

# Function to add a new task
def add_task():
    task_description = task_entry.get().strip()
    due_date = due_date_entry.get().strip()
    priority = priority_entry.get().strip()
    if not task_description:
        messagebox.showwarning("Input Error", "Please enter a task description.")
        return

    task = {
        "description": task_description,
        "due_date": due_date if due_date else None,
        "priority": priority if priority else "medium",
        "completed": False
    }

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)
    display_tasks()

# Function to display tasks
def display_tasks():
    tasks = load_tasks()
    tasks_listbox.delete(0, tk.END)
    for i, task in enumerate(tasks, start=1):
        status = "✓" if task["completed"] else "✗"
        tasks_listbox.insert(tk.END, f"{i}. [{status}] {task['description']} (Due: {task['due_date']}, Priority: {task['priority']})")

# Function to complete a task
def complete_task():
    selected_index = tasks_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Selection Error", "Please select a task to mark as completed.")
        return

    tasks = load_tasks()
    task_index = selected_index[0]
    tasks[task_index]["completed"] = True
    save_tasks(tasks)
    display_tasks()

# Function to remove a task
def remove_task():
    selected_index = tasks_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Selection Error", "Please select a task to remove.")
        return

    tasks = load_tasks()
    task_index = selected_index[0]
    tasks.pop(task_index)
    save_tasks(tasks)
    display_tasks()

# Function to update a task
def update_task():
    selected_index = tasks_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Selection Error", "Please select a task to update.")
        return

    tasks = load_tasks()
    task_index = selected_index[0]
    task = tasks[task_index]

    new_description = task_entry.get().strip()
    new_due_date = due_date_entry.get().strip()
    new_priority = priority_entry.get().strip()

    if new_description:
        task["description"] = new_description
    if new_due_date:
        task["due_date"] = new_due_date
    if new_priority:
        task["priority"] = new_priority

    tasks[task_index] = task
    save_tasks(tasks)
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)
    display_tasks()

# Function to add tooltips
def create_tooltip(widget, text):
    tooltip = ttk.Label(root, text=text, bootstyle="info", relief="solid", padding=5, font=("Helvetica", 10, "italic"))
    def show_tooltip(event):
        tooltip.place(x=event.x_root + 10, y=event.y_root + 10)
        tooltip.tkraise() #Bringing tooltip to the front
    def hide_tooltip(event):
        tooltip.place_forget()
    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

# Create the main window
root = ttk.Window(themename="cyborg")  # Use a ttkbootstrap theme
root.title("To-Do List App")
root.geometry("1150x625")  # Set the window size

# Create custom styles for buttons
style = ttk.Style()
style.configure("TButton", font=('Helvetica', 12))

# Create a Frame for entries
entry_frame = ttk.Frame(root)
entry_frame.pack(pady=10)

ttk.Label(entry_frame, text="Task Description:").grid(row=0, column=0, padx=(10, 0), pady=(0, 5), sticky="e")
task_entry = ttk.Entry(entry_frame, width=50, font=('Helvetica', 12))
task_entry.grid(row=0, column=1, padx=10, pady=(0, 5))

ttk.Label(entry_frame, text="Due Date (YYYY-MM-DD):").grid(row=1, column=0, padx=(10, 0), pady=5, sticky="e")
due_date_entry = ttk.Entry(entry_frame, width=50, font=('Helvetica', 12))
due_date_entry.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(entry_frame, text="Priority (low/medium/high):").grid(row=2, column=0, padx=(10, 0), pady=5, sticky="e")
priority_entry = ttk.Entry(entry_frame, width=50, font=('Helvetica', 12))
priority_entry.grid(row=2, column=1, padx=10, pady=5)

# Create a Frame for buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

add_button = ttk.Button(button_frame, text="Add Task", command=add_task, bootstyle=SUCCESS)
create_tooltip(add_button, "Click to add a new task")
add_button.grid(row=0, column=0, padx=5, pady=5)

complete_button = ttk.Button(button_frame, text="Mark Task as Completed", command=complete_task, bootstyle=INFO)
create_tooltip(complete_button, "Click to mark the selected task as completed")
complete_button.grid(row=0, column=1, padx=5, pady=5)

remove_button = ttk.Button(button_frame, text="Remove Task", command=remove_task, bootstyle=DANGER)
create_tooltip(remove_button, "Click to remove the selected task")
remove_button.grid(row=0, column=2, padx=5, pady=5)

update_button = ttk.Button(button_frame, text="Update Task", command=update_task, bootstyle=WARNING)
create_tooltip(update_button, "Click to update the selected task with new details")
update_button.grid(row=0, column=3, padx=5, pady=5)


# Create a Frame for the Listbox and Scrollbar
list_frame = ttk.Frame(root)
list_frame.pack(pady=10, fill=tk.BOTH, expand=False)

tasks_listbox = tk.Listbox(list_frame, width=80, height=15, font=('Helvetica', 12))
tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tasks_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tasks_listbox.config(yscrollcommand=scrollbar.set)

# Initial call to display tasks
display_tasks()

# Run the main loop
root.mainloop()
