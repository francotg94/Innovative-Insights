import json
import os
import tkinter as tk
from tkinter import messagebox
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
    task_description = input("Enter task description: ").strip()
    due_date = input("Enter due date (YYYY-MM-DD) or leave empty: ").strip()
    priority = input("Enter priority (low/medium/high) or leave empty: ").strip()

    task = {
        "description": task_description,
        "due_date": due_date if due_date else None,
        "priority": priority if priority else "medium",
        "completed": False
    }

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task '{task_description}' added!")

# Function to list all tasks
def list_tasks(show_completed=False):  # Default to show uncompleted tasks
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return

    print("Your Tasks:")
    for i, task in enumerate(tasks, start=1):
        # Initialize status based on completion status
        status = "✓" if task["completed"] else "✗"
        # Print the task details
        print(f"{i}. [{status}] {task['description']} (Due: {task['due_date']}, Priority: {task['priority']})")

# Function to mark a task as completed
def complete_task(task_number):
    tasks = load_tasks()
    if 0 < task_number <= len(tasks):
        tasks[task_number - 1]["completed"] = True
        save_tasks(tasks)
        print(f"Task {task_number} marked as completed!")
    else:
        print("Invalid task number.")

# Function to remove a task
def remove_task(task_number):
    tasks = load_tasks()
    if 0 < task_number <= len(tasks):
        removed_task = tasks.pop(task_number - 1)
        save_tasks(tasks)
        print(f"Task '{removed_task['description']}' removed!")
    else:
        print("Invalid task number.")

# Function to update an existing task
def update_task(task_number):
    tasks = load_tasks()
    if 0 < task_number <= len(tasks):
        task = tasks[task_number - 1]

        print(f"Current description: {task['description']}")
        new_description = input("Enter new description (leave empty to keep current): ").strip()
        if new_description:
            task["description"] = new_description

        print(f"Current due date: {task['due_date']}")
        new_due_date = input("Enter new due date (YYYY-MM-DD, leave empty to keep current): ").strip()
        if new_due_date:
            task["due_date"] = new_due_date

        print(f"Current priority: {task['priority']}")
        new_priority = input("Enter new priority (low/medium/high, leave empty to keep current): ").strip()
        if new_priority:
            task["priority"] = new_priority

        print(f"Current completion status: {'completed' if task['completed'] else 'not completed'}")
        mark_complete = input("Mark as completed? (y/n, leave empty to keep current): ").strip().lower()
        if mark_complete == 'y':
            task["completed"] = True
        elif mark_complete == 'n':
            task["completed"] = False

        save_tasks(tasks)
        print(f"Task {task_number} updated!")
    else:
        print("Invalid task number.")

# Main function to handle user commands
def main():
    while True:
        command = input("Enter command (add/list/list_completed/complete/remove/update/quit): ").strip().lower()
        if command == "add":
            add_task()
        elif command == "list":
            list_tasks(show_completed=False)  # Default to show only uncompleted tasks
        elif command == "list_completed":
            list_tasks(show_completed=True)
        elif command == "complete":
            try:
                task_number = int(input("Enter task number to mark as completed: ").strip())
                complete_task(task_number)
            except ValueError:
                print("Invalid input. Please enter a valid task number.")
        elif command == "remove":
            try:
                task_number = int(input("Enter task number to remove: ").strip())
                remove_task(task_number)
            except ValueError:
                print("Invalid input. Please enter a valid task number.")
        elif command == "update":
            try:
                task_number = int(input("Enter task number to update: ").strip())
                update_task(task_number)
            except ValueError:
                print("Invalid input. Please enter a valid task number.")
        elif command == "quit":
            print("Goodbye!")
            break
        else:
            print("Unknown command!")

# Entry point of the application
if __name__ == "__main__":
    main()