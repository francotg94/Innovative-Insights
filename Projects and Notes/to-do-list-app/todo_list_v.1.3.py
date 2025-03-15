import json
import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime, timedelta

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
    category = category_entry.get().strip()
    notes = notes_entry.get().strip()
    subtasks = subtasks_text.get("1.0", tk.END).strip().split("\n")
    if not task_description:
        messagebox.showwarning("Input Error", "Please enter a task description.")
        return

    task = {
        "description": task_description,
        "due_date": due_date if due_date else None,
        "priority": priority if priority else "medium",
        "category": category if category else "General",
        "notes": notes if notes else "",
        "subtasks": subtasks if subtasks else [],
        "completed": False
    }

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    notes_entry.delete(0, tk.END)
    subtasks_text.delete("1.0", tk.END)
    display_tasks()
    check_reminders()

# Function to display tasks
def display_tasks(filter_by_category=None):
    tasks = load_tasks()
    tasks_listbox.delete(0, tk.END)
    
    filtered_tasks = [task for task in tasks if filter_by_category is None or task.get("category", "General") == filter_by_category]
    
    for i, task in enumerate(filtered_tasks, start=1):
        status = "✓" if task["completed"] else "✗"
        task_info = f"{i}. [{status}] {task['description']} (Due: {task['due_date']}, Priority: {task['priority']}, Category: {task.get('category', 'General')})"
        tasks_listbox.insert(tk.END, task_info)
        # Display subtasks
        for j, subtask in enumerate(task.get("subtasks", []), start=1):
            subtask_status = "✓" if subtask.startswith("[✓]") else "✗"
            tasks_listbox.insert(tk.END, f"    {i}.{j}. [{subtask_status}] {subtask}")

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
    new_category = category_entry.get().strip()
    new_notes = notes_entry.get().strip()
    new_subtasks = subtasks_text.get("1.0", tk.END).strip().split("\n")

    if new_description:
        task["description"] = new_description
    if new_due_date:
        task["due_date"] = new_due_date
    if new_priority:
        task["priority"] = new_priority
    if new_category:
        task["category"] = new_category
    if new_notes:
        task["notes"] = new_notes
    if new_subtasks:
        task["subtasks"] = new_subtasks

    tasks[task_index] = task
    save_tasks(tasks)
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    notes_entry.delete(0, tk.END)
    subtasks_text.delete("1.0", tk.END)
    display_tasks()

# Function to check reminders for tasks due in the next 24 hours
def check_reminders():
    due_soon_timeframe = datetime.now() + timedelta(hours=24)
    tasks = load_tasks()
    due_soon_tasks = [task for task in tasks if task["due_date"] and datetime.strptime(task["due_date"], "%Y-%m-%d") <= due_soon_timeframe and not task["completed"]]
    
    if due_soon_tasks:
        message = "The following tasks are due soon:\n\n"
        message += "\n".join([f"{task['description']} (Due: {task['due_date']})" for task in due_soon_tasks])
        messagebox.showinfo("Task Reminders", message)

# Function to add tooltips
def create_tooltip(widget, text):
    tooltip = ttk.Label(root, text=text, bootstyle="info", relief="solid", padding=5, font=("Helvetica", 10, "italic"))
    tooltip.place_forget()

    def show_tooltip(event):
        tooltip.place(x=event.x_root + 10, y=event.y_root + 10)
        tooltip.tkraise()  # Bring tooltip to the front

    def hide_tooltip(event):
        tooltip.place_forget()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

# Search functionality
def search_tasks():
    search_term = search_entry.get().strip().lower()
    all_tasks = load_tasks()
    filtered_tasks = [task for task in all_tasks if search_term in task["description"].lower()]
    tasks_listbox.delete(0, tk.END)
    for i, task in enumerate(filtered_tasks, start=1):
        status = "✓" if task["completed"] else "✗"
        tasks_listbox.insert(tk.END, f"{i}. [{status}] {task['description']} (Due: {task['due_date']}, Priority: {task['priority']}, Category: {task.get('category', 'General')})")

# Filter by category functionality
def filter_by_category():
    selected_category = category_filter.get()
    display_tasks(filter_by_category=selected_category)

# Create the main window
root = ttk.Window(themename="superhero")  # Use a ttkbootstrap theme
root.title("To-Do List App")
root.geometry("600x700")  # Set the window size

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

ttk.Label(entry_frame, text="Category:").grid(row=3, column=0, padx=(10, 0), pady=5, sticky="e")
category_entry = ttk.Entry(entry_frame, width=50, font=('Helvetica', 12))
category_entry.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(entry_frame, text="Notes:").grid(row=4, column=0, padx=(10, 0), pady=5, sticky="e")
notes_entry = ttk.Entry(entry_frame, width=50, font=('Helvetica', 12))
notes_entry.grid(row=4, column=1, padx=10, pady=5)

ttk.Label(entry_frame, text="Subtasks (one per line):").grid(row=5, column=0, padx=(10, 0), pady=5, sticky="ne")
subtasks_text = tk.Text(entry_frame, width=50, height=5, font=('Helvetica', 12))
subtasks_text.grid(row=5, column=1, padx=10, pady=5)

# Create a Frame for search and filter options
filter_frame = ttk.Frame(root)
filter_frame.pack(pady=10)

ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, padx=(10, 0), pady=5, sticky="e")
search_entry = ttk.Entry(filter_frame, width=30, font=('Helvetica', 12))
search_entry.grid(row=0, column=1, padx=10, pady=5)
search_button = ttk.Button(filter_frame, text="Search", command=search_tasks, bootstyle=PRIMARY)
search_button.grid(row=0, column=2, padx=5, pady=5)
create_tooltip(search_button, "Click to search tasks by description")

ttk.Label(filter_frame, text="Category Filter:").grid(row=1, column=0, padx=(10, 0), pady=5, sticky="e")
category_filter = ttk.Combobox(filter_frame, values=["General", "Work", "Personal", "Urgent"], font=('Helvetica', 12))
category_filter.grid(row=1, column=1, padx=10, pady=5)
filter_button = ttk.Button(filter_frame, text="Filter", command=filter_by_category, bootstyle=PRIMARY)
filter_button.grid(row=1, column=2, padx=5, pady=5)
create_tooltip(filter_button, "Click to filter tasks by category")

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
list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

tasks_listbox = tk.Listbox(list_frame, width=80, height=15, font=('Helvetica', 12))
tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tasks_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tasks_listbox.config(yscrollcommand=scrollbar.set)

# Initial call to display tasks and set reminders
display_tasks()
check_reminders()

# Run the main loop
root.mainloop()
