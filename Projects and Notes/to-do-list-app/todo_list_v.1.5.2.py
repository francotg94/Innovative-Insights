import json
import os
import sys
import re
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

undo_stack = []
redo_stack = []

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_tasks():
    if not os.path.exists("tasks.json"):
        return []
    try:
        with open("tasks.json", "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Failed to load tasks. The JSON file might be corrupt.")
        return []
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []

def save_tasks(tasks):
    global undo_stack, redo_stack
    undo_stack.append(load_tasks())  # push current state to undo stack
    redo_stack.clear()  # clear redo stack whenever a new action is performed
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)
    backup_tasks()

def backup_tasks():
    backup_path = "tasks_backup.json"
    try:
        shutil.copy("tasks.json", backup_path)
    except Exception as e:
        messagebox.showerror("Backup Error", f"Failed to create a backup: {str(e)}")

def display_tasks(filter_by_category=None):
    tasks = load_tasks()
    tasks_listbox.delete(0, tk.END)
    
    filtered_tasks = [task for task in tasks if filter_by_category is None or filter_by_category == 'All' or task.get("category", "General") == filter_by_category]
    
    for i, task in enumerate(filtered_tasks, start=1):
        status = "✓" if task["completed"] else "✗"
        priority_color = "green" if task["priority"] == "low" else "orange" if task["priority"] == "medium" else "red"
        task_info = f"{i}. [{status}] {task['description']} (Due: {task['due_date']}, Priority: {task['priority']}, Category: {task.get('category', 'General')})"
        tasks_listbox.insert(tk.END, task_info)
        tasks_listbox.itemconfig(tk.END, {'bg': priority_color})
        for j, subtask in enumerate(task.get("subtasks", []), start=1):
            subtask_status = "✓" if subtask.startswith("[✓]") else "✗"
            tasks_listbox.insert(tk.END, f"    {i}.{j}. [{subtask_status}] {subtask}")

def add_task():
    task_description = task_entry.get().strip()
    due_date = due_date_entry.get().strip()
    priority = priority_entry.get().strip().lower()
    category = category_entry.get().strip()
    notes = notes_entry.get().strip()
    subtasks = subtasks_text.get("1.0", tk.END).strip().split("\n")

    if not task_description:
        messagebox.showwarning("Input Error", "Please enter a task description.")
        return

    if due_date and not re.match(r'\d{4}-\d{2}-\d{2}', due_date):
        messagebox.showwarning("Input Error", "Please enter a valid due date (YYYY-MM-DD).")
        return

    if priority and priority not in ["low", "medium", "high"]:
        messagebox.showwarning("Input Error", "Please enter a valid priority (low, medium, high).")
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

def sort_tasks_by_due_date():
    tasks = load_tasks()
    tasks.sort(key=lambda task: (task['due_date'] is None, task['due_date']))
    save_tasks(tasks)
    display_tasks()

def sort_tasks_by_priority():
    priority_map = {'low': 0, 'medium': 1, 'high': 2}
    tasks = load_tasks()
    tasks.sort(key=lambda task: priority_map.get(task.get('priority', 'medium'), 1))
    save_tasks(tasks)
    display_tasks()

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

def check_reminders():
    due_soon_timeframe = datetime.now() + timedelta(hours=24)
    tasks = load_tasks()
    due_soon_tasks = [task for task in tasks if task["due_date"] and datetime.strptime(task["due_date"], "%Y-%m-%d") <= due_soon_timeframe and not task["completed"]]
    
    if due_soon_tasks:
        message = "The following tasks are due soon:\n\n"
        message += "\n".join([f"{task['description']} (Due: {task['due_date']})" for task in due_soon_tasks])
        messagebox.showinfo("Task Reminders", message)

def show_help():
    messagebox.showinfo("Help", "User manual and help go here...")

def about():
    messagebox.showinfo("About", "To-Do List App v1.5\n\nA simple to-do list application to manage tasks effectively.")

def create_tooltip(widget, text):
    tooltip = ttk.Label(root, text=text, bootstyle="info", relief="solid", padding=5, font=("Helvetica", 10, "italic"))
    tooltip.place_forget()

    def show_tooltip(event):
        tooltip.place(x=event.x_root + 10, y=event.y_root + 10)
        tooltip.tkraise()

    def hide_tooltip(event):
        tooltip.place_forget()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

def search_tasks():
    search_term = search_entry.get().strip().lower()
    selected_category = category_filter.get()
    all_tasks = load_tasks()
    
    def match(task):
        return search_term in task["description"].lower() and (selected_category == "All" or task["category"] == selected_category)
    
    filtered_tasks = [task for task in all_tasks if match(task)]
    
    tasks_listbox.delete(0, tk.END)
    for i, task in enumerate(filtered_tasks, start=1):
        status = "✓" if task["completed"] else "✗"
        tasks_listbox.insert(tk.END, f"{i}. [{status}] {task['description']} (Due: {task['due_date']}, Priority: {task['priority']}, Category: {task.get('category', 'General')})")

def filter_by_category():
    selected_category = category_filter.get()
    display_tasks(filter_by_category=selected_category)

def new_file():
    tasks_listbox.delete(0, tk.END)
    save_tasks([])

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            tasks = json.load(file)
            save_tasks(tasks)
            display_tasks()

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        tasks = load_tasks()
        with open(file_path, "w") as file:
            json.dump(tasks, file, indent=4)
        messagebox.showinfo("Save Successful", f"Tasks have been saved to {file_path}")

def export_tasks():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        tasks = load_tasks()
        with open(file_path, "w") as file:
            file.write("Description,Due Date,Priority,Category,Notes,Completed,Subtasks\n")
            for task in tasks:
                subtasks = ";".join(task["subtasks"])
                file.write(f"{task['description']},{task['due_date']},{task['priority']},{task['category']},{task['notes']},{task['completed']},{subtasks}\n")
        messagebox.showinfo("Export Successful", f"Tasks have been exported to {file_path}")

def import_tasks():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if file_path:
        tasks = load_tasks()
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines[1:]:
                description, due_date, priority, category, notes, completed, subtasks = line.strip().split(",")
                task = {
                    "description": description,
                    "due_date": due_date,
                    "priority": priority,
                    "category": category,
                    "notes": notes,
                    "completed": completed == "True",
                    "subtasks": subtasks.split(";")
                }
                tasks.append(task)
        save_tasks(tasks)
        display_tasks()
        messagebox.showinfo("Import Successful", "Tasks have been imported successfully")

def undo():
    global undo_stack, redo_stack

    if not undo_stack:
        messagebox.showinfo("Undo", "No actions to undo.")
        return

    current_state = load_tasks()
    redo_stack.append(current_state)  # push current state to redo stack
    previous_state = undo_stack.pop()
    with open("tasks.json", "w") as file:
        json.dump(previous_state, file, indent=4)
    display_tasks()
    messagebox.showinfo("Undo", "Action undone successfully.")

def redo():
    global undo_stack, redo_stack

    if not redo_stack:
        messagebox.showinfo("Redo", "No actions to redo.")
        return

    current_state = load_tasks()
    undo_stack.append(current_state)  # push current state to undo stack
    next_state = redo_stack.pop()
    with open("tasks.json", "w") as file:
        json.dump(next_state, file, indent=4)
    display_tasks()
    messagebox.showinfo("Redo", "Action redone successfully.")

root = ttk.Window(themename="superhero")
root.title("To-Do List App")
root.geometry("1150x625")

add_icon = ImageTk.PhotoImage(Image.open(resource_path("add_icon.png")).resize((20, 20)))
complete_icon = ImageTk.PhotoImage(Image.open(resource_path("complete_icon.png")).resize((20, 20)))
remove_icon = ImageTk.PhotoImage(Image.open(resource_path("remove_icon.png")).resize((20, 20)))
update_icon = ImageTk.PhotoImage(Image.open(resource_path("update_icon.png")).resize((20, 20)))
export_icon = ImageTk.PhotoImage(Image.open(resource_path("export_icon.png")).resize((20, 20)))
import_icon = ImageTk.PhotoImage(Image.open(resource_path("import_icon.png")).resize((20, 20)))

menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Undo", command=undo)
edit_menu.add_command(label="Redo", command=redo)
edit_menu.add_separator()
edit_menu.add_command(label="Search", command=search_tasks)
edit_menu.add_command(label="Delete", command=remove_task)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

view_menu = Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Sort By Due Date", command=sort_tasks_by_due_date)
view_menu.add_command(label="Sort By Priority", command=sort_tasks_by_priority)
menu_bar.add_cascade(label="View", menu=view_menu)

help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label="User Manual", command=show_help)
help_menu.add_command(label="About", command=about)
menu_bar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menu_bar)

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

filter_frame = ttk.Frame(root)
filter_frame.pack(pady=10)

ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, padx=(10, 0), pady=5, sticky="e")
search_entry = ttk.Entry(filter_frame, width=30, font=('Helvetica', 12))
search_entry.grid(row=0, column=1, padx=10, pady=5)
search_button = ttk.Button(filter_frame, text="Search", command=search_tasks, bootstyle=PRIMARY)
search_button.grid(row=0, column=2, padx=5, pady=5)
create_tooltip(search_button, "Click to search tasks by description")

ttk.Label(filter_frame, text="Category Filter:").grid(row=1, column=0, padx=(10, 0), pady=5, sticky="e")
category_filter = ttk.Combobox(filter_frame, values=["All", "General", "Work Order", "Planned Event", "Personal", "Urgent"], font=('Helvetica', 12))
category_filter.grid(row=1, column=1, padx=10, pady=5)
category_filter.set("All")
filter_button = ttk.Button(filter_frame, text="Filter", command=filter_by_category, bootstyle=PRIMARY)
filter_button.grid(row=1, column=2, padx=5, pady=5)
create_tooltip(filter_button, "Click to filter tasks by category")

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

add_button = ttk.Button(button_frame, text="Add Task", image=add_icon, compound=tk.LEFT, command=add_task, bootstyle=SUCCESS)
create_tooltip(add_button, "Click to add a new task")
add_button.grid(row=0, column=0, padx=5, pady=5)

complete_button = ttk.Button(button_frame, text="Mark Completed", image=complete_icon, compound=tk.LEFT, command=complete_task, bootstyle=INFO)
create_tooltip(complete_button, "Click to mark the selected task as completed")
complete_button.grid(row=0, column=1, padx=5, pady=5)

remove_button = ttk.Button(button_frame, text="Remove Task", image=remove_icon, compound=tk.LEFT, command=remove_task, bootstyle=DANGER)
create_tooltip(remove_button, "Click to remove the selected task")
remove_button.grid(row=0, column=2, padx=5, pady=5)

update_button = ttk.Button(button_frame, text="Update Task", image=update_icon, compound=tk.LEFT, command=update_task, bootstyle=WARNING)
create_tooltip(update_button, "Click to update the selected task with new details")
update_button.grid(row=0, column=3, padx=5, pady=5)

export_button = ttk.Button(button_frame, text="Export Tasks", image=export_icon, compound=tk.LEFT, command=export_tasks, bootstyle=PRIMARY)
create_tooltip(export_button, "Click to export tasks to a CSV file")
export_button.grid(row=0, column=4, padx=5, pady=5)

import_button = ttk.Button(button_frame, text="Import Tasks", image=import_icon, compound=tk.LEFT, command=import_tasks, bootstyle=PRIMARY)
create_tooltip(import_button, "Click to import tasks from a CSV file")
import_button.grid(row=0, column=5, padx=5, pady=5)

list_frame = ttk.Frame(root)
list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

tasks_listbox = tk.Listbox(list_frame, width=110, height=15, font=('Helvetica', 12))
tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tasks_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tasks_listbox.config(yscrollcommand=scrollbar.set)

display_tasks()
check_reminders()

root.mainloop()
