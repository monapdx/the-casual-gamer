import tkinter as tk
from tkinter import messagebox
import json
from cryptography.fernet import Fernet
import os

# --- Setup encryption key ---
KEY_FILE = "key.key"
DATA_FILE = "passwords.json"

# Generate key if not exists
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

fernet = Fernet(key)

# --- Load existing passwords ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        passwords = json.load(f)
else:
    passwords = []

# --- GUI ---
def save_password():
    url = url_entry.get()
    username = user_entry.get()
    password = pass_entry.get()

    if not url or not username or not password:
        messagebox.showwarning("Error", "Please fill all fields")
        return

    encrypted_password = fernet.encrypt(password.encode()).decode()
    passwords.append({"url": url, "username": username, "password": encrypted_password})

    with open(DATA_FILE, "w") as f:
        json.dump(passwords, f)

    update_listbox()
    url_entry.delete(0, tk.END)
    user_entry.delete(0, tk.END)
    pass_entry.delete(0, tk.END)

def update_listbox():
    listbox.delete(0, tk.END)
    for item in passwords:
        listbox.insert(tk.END, f"{item['url']} | {item['username']}")

def show_password(event):
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        encrypted = passwords[index]['password']
        decrypted = fernet.decrypt(encrypted.encode()).decode()
        messagebox.showinfo("Password", f"Password: {decrypted}")

root = tk.Tk()
root.title("Simple Password Manager")

tk.Label(root, text="URL:").grid(row=0, column=0)
url_entry = tk.Entry(root, width=40)
url_entry.grid(row=0, column=1)

tk.Label(root, text="Username:").grid(row=1, column=0)
user_entry = tk.Entry(root, width=40)
user_entry.grid(row=1, column=1)

tk.Label(root, text="Password:").grid(row=2, column=0)
pass_entry = tk.Entry(root, width=40)
pass_entry.grid(row=2, column=1)

tk.Button(root, text="Save Password", command=save_password).grid(row=3, column=0, columnspan=2, pady=10)

listbox = tk.Listbox(root, width=60)
listbox.grid(row=4, column=0, columnspan=2)
listbox.bind("<Double-1>", show_password)

update_listbox()
root.mainloop()
