import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
from datetime import datetime
import csv
import os
import json

# Set appearance
ctk.set_appearance_mode("System")  # Can be "System", "Dark", or "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

# Database file
DATABASE_FILE = "organization_data.json"

# Default data structure
default_data = {
    "members": [],
    "events": [],
    "donations": [],
    "blood_donations": [],
    "users": {"123456": "123456"}  # Default admin credentials
}

# Load or initialize database
def load_database():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_data
    return default_data

def save_database(data):
    try:
        with open(DATABASE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except IOError:
        return False

# Global database
db = load_database()
members = db["members"]
events = db["events"]
donations = db["donations"]
blood_donations = db["blood_donations"]
users = db["users"]

class OrganizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organization Database Management System")
        self.root.geometry("1200x800")
        
        # Menu bar
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Backup Data", command=self.backup_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Create tab view
        self.tabview = ctk.CTkTabview(root)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Add tabs
        self.tabview.add("Members")
        self.tabview.add("Events")
        self.tabview.add("Donations")
        self.tabview.add("Blood Donations")
        
        # Configure each tab
        self.setup_members_tab()
        self.setup_events_tab()
        self.setup_donations_tab()
        self.setup_blood_donations_tab()
        
        # Status bar
        self.status_var = ctk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ctk.CTkLabel(root, textvariable=self.status_var, anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # Auto-save timer
        self.auto_save()
    
    def auto_save(self):
        self.save_data()
        self.root.after(300000, self.auto_save)  # Auto-save every 5 minutes
    
    def save_data(self):
        db = {
            "members": members,
            "events": events,
            "donations": donations,
            "blood_donations": blood_donations,
            "users": users
        }
        if save_database(db):
            self.update_status("Data saved successfully")
        else:
            self.update_status("Error saving data", error=True)
    
    def backup_data(self):
        backup_file = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save backup file"
        )
        if backup_file:
            db = {
                "members": members,
                "events": events,
                "donations": donations,
                "blood_donations": blood_donations,
                "users": users
            }
            try:
                with open(backup_file, "w") as f:
                    json.dump(db, f, indent=2)
                self.update_status(f"Backup saved to {backup_file}")
            except IOError:
                self.update_status("Error saving backup", error=True)
    
    def export_data(self):
        # Ask which data to export
        export_type = tk.StringVar(value="members")
        
        export_dialog = ctk.CTkToplevel(self.root)
        export_dialog.title("Export Data")
        export_dialog.geometry("400x300")
        export_dialog.transient(self.root)
        export_dialog.grab_set()
        
        ctk.CTkLabel(export_dialog, text="Select data to export:", font=("Arial", 14)).pack(pady=10)
        
        options = [
            ("Members", "members"),
            ("Events", "events"),
            ("Donations", "donations"),
            ("Blood Donations", "blood_donations")
        ]
        
        for text, value in options:
            ctk.CTkRadioButton(export_dialog, text=text, variable=export_type, value=value).pack(anchor="w", padx=20, pady=5)
        
        def perform_export():
            data_type = export_type.get()
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title=f"Export {data_type} to CSV"
            )
            if filename:
                try:
                    if data_type == "members":
                        data = members
                        fieldnames = ["id", "name", "email", "phone", "address"]
                    elif data_type == "events":
                        data = events
                        fieldnames = ["id", "name", "date", "location", "description"]
                    elif data_type == "donations":
                        data = donations
                        fieldnames = ["id", "donor_name", "amount", "date"]
                    elif data_type == "blood_donations":
                        data = blood_donations
                        fieldnames = ["id", "donor_name", "blood_group", "donation_date"]
                    
                    with open(filename, "w", newline="") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(data)
                    
                    self.update_status(f"{data_type.capitalize()} exported to {filename}")
                    export_dialog.destroy()
                except Exception as e:
                    self.update_status(f"Export failed: {str(e)}", error=True)
        
        ctk.CTkButton(export_dialog, text="Export", command=perform_export).pack(pady=20)
    
    def update_status(self, message, error=False):
        self.status_var.set(message)
        if error:
            self.status_bar.configure(text_color="red")
        else:
            self.status_bar.configure(text_color="green")
        self.root.after(5000, lambda: (self.status_var.set("Ready"), self.status_bar.configure(text_color="gray")))
    
    def setup_members_tab(self):
        tab = self.tabview.tab("Members")
        
        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.member_search_entry = ctk.CTkEntry(search_frame)
        self.member_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.member_search_entry.bind("<KeyRelease>", lambda e: self.search_members())
        
        ctk.CTkButton(search_frame, text="Clear", width=80, command=self.clear_member_search).pack(side="left", padx=5)
        
        # Add/edit member frame
        add_frame = ctk.CTkFrame(tab)
        add_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(add_frame, text="Member Details", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Entry fields
        fields = ["Name", "Email", "Phone", "Address", "Password"]
        self.member_entries = {}
        for field in fields:
            frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(frame, text=f"{field}:").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", expand=True, fill="x", padx=5)
            self.member_entries[field.lower()] = entry
        
        # Password field should show asterisks
        self.member_entries["password"].configure(show="*")
        
        # Buttons frame
        button_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        button_frame.pack(pady=10, fill="x")
        
        ctk.CTkButton(button_frame, text="Add Member", command=self.add_member).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Update Member", command=self.update_member).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clear", command=self.clear_member_fields).pack(side="left", padx=5)
        
        # View/Delete members frame
        view_frame = ctk.CTkFrame(tab)
        view_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Treeview for members
        columns = ("ID", "Name", "Email", "Phone", "Address")
        self.member_tree = ttk.Treeview(view_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.member_tree.heading(col, text=col)
            self.member_tree.column(col, width=100, anchor="w")
        
        self.member_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Bind treeview selection
        self.member_tree.bind("<<TreeviewSelect>>", self.on_member_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.member_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.member_tree.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        del_button_frame = ctk.CTkFrame(tab)
        del_button_frame.pack(pady=5)
        ctk.CTkButton(del_button_frame, text="Delete Selected", command=self.delete_member, 
                      fg_color="#d9534f", hover_color="#c9302c").pack(side="left", padx=5)
        ctk.CTkButton(del_button_frame, text="Refresh List", command=self.refresh_members).pack(side="left", padx=5)
        
        # Load initial data
        self.refresh_members()
    
    def setup_events_tab(self):
        tab = self.tabview.tab("Events")
        
        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.event_search_entry = ctk.CTkEntry(search_frame)
        self.event_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.event_search_entry.bind("<KeyRelease>", lambda e: self.search_events())
        
        ctk.CTkButton(search_frame, text="Clear", width=80, command=self.clear_event_search).pack(side="left", padx=5)
        
        # Add/edit event frame
        add_frame = ctk.CTkFrame(tab)
        add_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(add_frame, text="Event Details", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Entry fields
        fields = ["Name", "Date (YYYY-MM-DD)", "Location", "Description"]
        self.event_entries = {}
        for field in fields:
            frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(frame, text=f"{field.split(' ')[0]}:").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", expand=True, fill="x", padx=5)
            self.event_entries[field.split(' ')[0].lower()] = entry
        
        # Buttons frame
        button_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        button_frame.pack(pady=10, fill="x")
        
        ctk.CTkButton(button_frame, text="Add Event", command=self.add_event).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Update Event", command=self.update_event).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clear", command=self.clear_event_fields).pack(side="left", padx=5)
        
        # View events frame
        view_frame = ctk.CTkFrame(tab)
        view_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Treeview for events
        columns = ("ID", "Name", "Date", "Location", "Description")
        self.event_tree = ttk.Treeview(view_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.event_tree.heading(col, text=col)
            self.event_tree.column(col, width=100, anchor="w")
        
        self.event_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Bind treeview selection
        self.event_tree.bind("<<TreeviewSelect>>", self.on_event_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.event_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.event_tree.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="Delete Selected", command=self.delete_event, 
                      fg_color="#d9534f", hover_color="#c9302c").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Refresh List", command=self.refresh_events).pack(side="left", padx=5)
        
        # Load initial data
        self.refresh_events()
    
    def setup_donations_tab(self):
        tab = self.tabview.tab("Donations")
        
        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.donation_search_entry = ctk.CTkEntry(search_frame)
        self.donation_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.donation_search_entry.bind("<KeyRelease>", lambda e: self.search_donations())
        
        ctk.CTkButton(search_frame, text="Clear", width=80, command=self.clear_donation_search).pack(side="left", padx=5)
        
        # Add/edit donation frame
        add_frame = ctk.CTkFrame(tab)
        add_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(add_frame, text="Donation Details", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Entry fields
        fields = ["Donor Name", "Amount", "Date (YYYY-MM-DD)"]
        self.donation_entries = {}
        for field in fields:
            frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(frame, text=f"{field.split(' ')[0]}:").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", expand=True, fill="x", padx=5)
            self.donation_entries[field.split(' ')[0].lower()] = entry
        
        # Buttons frame
        button_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        button_frame.pack(pady=10, fill="x")
        
        ctk.CTkButton(button_frame, text="Add Donation", command=self.add_donation).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Update Donation", command=self.update_donation).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clear", command=self.clear_donation_fields).pack(side="left", padx=5)
        
        # View donations frame
        view_frame = ctk.CTkFrame(tab)
        view_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Treeview for donations
        columns = ("ID", "Donor Name", "Amount", "Date")
        self.donation_tree = ttk.Treeview(view_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.donation_tree.heading(col, text=col)
            self.donation_tree.column(col, width=100, anchor="w")
        
        self.donation_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Bind treeview selection
        self.donation_tree.bind("<<TreeviewSelect>>", self.on_donation_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.donation_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.donation_tree.configure(yscrollcommand=scrollbar.set)
        
        # Summary frame
        summary_frame = ctk.CTkFrame(tab)
        summary_frame.pack(pady=5, padx=10, fill="x")
        
        self.total_donations_var = ctk.StringVar()
        self.total_donations_var.set("Total Donations: $0.00")
        ctk.CTkLabel(summary_frame, textvariable=self.total_donations_var, font=("Arial", 12)).pack(side="left", padx=5)
        
        # Button frame
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="Delete Selected", command=self.delete_donation, 
                      fg_color="#d9534f", hover_color="#c9302c").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Refresh List", command=self.refresh_donations).pack(side="left", padx=5)
        
        # Load initial data
        self.refresh_donations()
    
    def setup_blood_donations_tab(self):
        tab = self.tabview.tab("Blood Donations")
        
        # Search frame
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.blood_donation_search_entry = ctk.CTkEntry(search_frame)
        self.blood_donation_search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.blood_donation_search_entry.bind("<KeyRelease>", lambda e: self.search_blood_donations())
        
        ctk.CTkButton(search_frame, text="Clear", width=80, command=self.clear_blood_donation_search).pack(side="left", padx=5)
        
        # Add/edit blood donation frame
        add_frame = ctk.CTkFrame(tab)
        add_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(add_frame, text="Blood Donation Details", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Entry fields
        fields = ["Donor Name", "Blood Group", "Donation Date (YYYY-MM-DD)"]
        self.blood_donation_entries = {}
        for field in fields:
            frame = ctk.CTkFrame(add_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(frame, text=f"{field.split(' ')[0]}:").pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", expand=True, fill="x", padx=5)
            self.blood_donation_entries[field.split(' ')[0].lower()] = entry
        
        # Buttons frame
        button_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        button_frame.pack(pady=10, fill="x")
        
        ctk.CTkButton(button_frame, text="Add Blood Donation", command=self.add_blood_donation).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Update Blood Donation", command=self.update_blood_donation).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clear", command=self.clear_blood_donation_fields).pack(side="left", padx=5)
        
        # View blood donations frame
        view_frame = ctk.CTkFrame(tab)
        view_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Treeview for blood donations
        columns = ("ID", "Donor Name", "Blood Group", "Donation Date")
        self.blood_donation_tree = ttk.Treeview(view_frame, columns=columns, show="headings", selectmode="browse")
        
        for col in columns:
            self.blood_donation_tree.heading(col, text=col)
            self.blood_donation_tree.column(col, width=100, anchor="w")
        
        self.blood_donation_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Bind treeview selection
        self.blood_donation_tree.bind("<<TreeviewSelect>>", self.on_blood_donation_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.blood_donation_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.blood_donation_tree.configure(yscrollcommand=scrollbar.set)
        
        # Summary frame
        summary_frame = ctk.CTkFrame(tab)
        summary_frame.pack(pady=5, padx=10, fill="x")
        
        self.total_blood_donations_var = ctk.StringVar()
        self.total_blood_donations_var.set("Total Blood Donations: 0")
        ctk.CTkLabel(summary_frame, textvariable=self.total_blood_donations_var, font=("Arial", 12)).pack(side="left", padx=5)
        
        # Button frame
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="Delete Selected", command=self.delete_blood_donation, 
                      fg_color="#d9534f", hover_color="#c9302c").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Refresh List", command=self.refresh_blood_donations).pack(side="left", padx=5)
        
        # Load initial data
        self.refresh_blood_donations()
    
    # Database operations
    def add_member(self):
        try:
            name = self.member_entries["name"].get()
            email = self.member_entries["email"].get()
            phone = self.member_entries["phone"].get()
            address = self.member_entries["address"].get()
            password = self.member_entries["password"].get()
            
            if not all([name, email, phone, address, password]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Check if email already exists
            if any(member["email"] == email for member in members):
                messagebox.showerror("Error", "Email already exists!")
                return
            
            member_id = max([member["id"] for member in members], default=0) + 1
            member = {
                "id": member_id,
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "password": password
            }
            members.append(member)
            
            # Clear entries
            self.clear_member_fields()
            
            self.refresh_members()
            self.save_data()
            self.update_status(f"Member '{name}' added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def update_member(self):
        selected_item = self.member_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a member to update")
            return
        
        try:
            item = self.member_tree.item(selected_item)
            member_id = item["values"][0]
            
            name = self.member_entries["name"].get()
            email = self.member_entries["email"].get()
            phone = self.member_entries["phone"].get()
            address = self.member_entries["address"].get()
            password = self.member_entries["password"].get()
            
            if not all([name, email, phone, address, password]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Find and update member
            for member in members:
                if member["id"] == member_id:
                    # Check if email is being changed to one that already exists
                    if member["email"] != email and any(m["email"] == email for m in members):
                        messagebox.showerror("Error", "Email already exists!")
                        return
                    
                    member["name"] = name
                    member["email"] = email
                    member["phone"] = phone
                    member["address"] = address
                    member["password"] = password
                    break
            
            self.refresh_members()
            self.save_data()
            self.update_status(f"Member '{name}' updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_member(self):
        selected_item = self.member_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a member to delete")
            return
        
        item = self.member_tree.item(selected_item)
        member_id = item["values"][0]
        member_name = item["values"][1]
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {member_name}?")
        if confirm:
            global members
            members = [member for member in members if member["id"] != member_id]
            self.clear_member_fields()
            self.refresh_members()
            self.save_data()
            self.update_status(f"Member '{member_name}' deleted successfully.")
    
    def add_event(self):
        try:
            name = self.event_entries["name"].get()
            date_str = self.event_entries["date"].get()
            location = self.event_entries["location"].get()
            description = self.event_entries["description"].get()
            
            if not all([name, date_str, location]):
                messagebox.showerror("Error", "Name, Date, and Location are required!")
                return
            
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            event_id = max([event["id"] for event in events], default=0) + 1
            event = {
                "id": event_id,
                "name": name,
                "date": date_str,
                "location": location,
                "description": description
            }
            events.append(event)
            
            # Clear entries
            self.clear_event_fields()
            
            self.refresh_events()
            self.save_data()
            self.update_status(f"Event '{name}' added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def update_event(self):
        selected_item = self.event_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an event to update")
            return
        
        try:
            item = self.event_tree.item(selected_item)
            event_id = item["values"][0]
            
            name = self.event_entries["name"].get()
            date_str = self.event_entries["date"].get()
            location = self.event_entries["location"].get()
            description = self.event_entries["description"].get()
            
            if not all([name, date_str, location]):
                messagebox.showerror("Error", "Name, Date, and Location are required!")
                return
            
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            # Find and update event
            for event in events:
                if event["id"] == event_id:
                    event["name"] = name
                    event["date"] = date_str
                    event["location"] = location
                    event["description"] = description
                    break
            
            self.refresh_events()
            self.save_data()
            self.update_status(f"Event '{name}' updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_event(self):
        selected_item = self.event_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an event to delete")
            return
        
        item = self.event_tree.item(selected_item)
        event_id = item["values"][0]
        event_name = item["values"][1]
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete {event_name}?")
        if confirm:
            global events
            events = [event for event in events if event["id"] != event_id]
            self.clear_event_fields()
            self.refresh_events()
            self.save_data()
            self.update_status(f"Event '{event_name}' deleted successfully.")
    
    def add_donation(self):
        try:
            donor_name = self.donation_entries["donor"].get()
            amount_str = self.donation_entries["amount"].get()
            date_str = self.donation_entries["date"].get()
            
            if not all([donor_name, amount_str, date_str]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Validate amount
            try:
                amount = float(amount_str)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number")
                return
            
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            donation_id = max([donation["id"] for donation in donations], default=0) + 1
            donation = {
                "id": donation_id,
                "donor_name": donor_name,
                "amount": amount,
                "date": date_str
            }
            donations.append(donation)
            
            # Clear entries
            self.clear_donation_fields()
            
            self.refresh_donations()
            self.save_data()
            self.update_status(f"Donation from '{donor_name}' added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def update_donation(self):
        selected_item = self.donation_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a donation to update")
            return
        
        try:
            item = self.donation_tree.item(selected_item)
            donation_id = item["values"][0]
            
            donor_name = self.donation_entries["donor"].get()
            amount_str = self.donation_entries["amount"].get()
            date_str = self.donation_entries["date"].get()
            
            if not all([donor_name, amount_str, date_str]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Validate amount
            try:
                amount = float(amount_str)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number")
                return
            
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            # Find and update donation
            for donation in donations:
                if donation["id"] == donation_id:
                    donation["donor_name"] = donor_name
                    donation["amount"] = amount
                    donation["date"] = date_str
                    break
            
            self.refresh_donations()
            self.save_data()
            self.update_status(f"Donation from '{donor_name}' updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_donation(self):
        selected_item = self.donation_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a donation to delete")
            return
        
        item = self.donation_tree.item(selected_item)
        donation_id = item["values"][0]
        donor_name = item["values"][1]
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete donation from {donor_name}?")
        if confirm:
            global donations
            donations = [donation for donation in donations if donation["id"] != donation_id]
            self.clear_donation_fields()
            self.refresh_donations()
            self.save_data()
            self.update_status(f"Donation from '{donor_name}' deleted successfully.")
    
    def add_blood_donation(self):
        try:
            donor_name = self.blood_donation_entries["donor"].get()
            blood_group = self.blood_donation_entries["blood"].get()
            date_str = self.blood_donation_entries["donation"].get()
            
            if not all([donor_name, blood_group, date_str]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            blood_donation_id = max([bd["id"] for bd in blood_donations], default=0) + 1
            blood_donation = {
                "id": blood_donation_id,
                "donor_name": donor_name,
                "blood_group": blood_group,
                "donation_date": date_str
            }
            blood_donations.append(blood_donation)
            
            # Clear entries
            self.clear_blood_donation_fields()
            
            self.refresh_blood_donations()
            self.save_data()
            self.update_status(f"Blood donation from '{donor_name}' added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def update_blood_donation(self):
        selected_item = self.blood_donation_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a blood donation to update")
            return
        
        try:
            item = self.blood_donation_tree.item(selected_item)
            blood_donation_id = item["values"][0]
            
            donor_name = self.blood_donation_entries["donor"].get()
            blood_group = self.blood_donation_entries["blood"].get()
            date_str = self.blood_donation_entries["donation"].get()
            
            if not all([donor_name, blood_group, date_str]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return
            
            # Find and update blood donation
            for bd in blood_donations:
                if bd["id"] == blood_donation_id:
                    bd["donor_name"] = donor_name
                    bd["blood_group"] = blood_group
                    bd["donation_date"] = date_str
                    break
            
            self.refresh_blood_donations()
            self.save_data()
            self.update_status(f"Blood donation from '{donor_name}' updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_blood_donation(self):
        selected_item = self.blood_donation_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a blood donation to delete")
            return
        
        item = self.blood_donation_tree.item(selected_item)
        blood_donation_id = item["values"][0]
        donor_name = item["values"][1]
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete blood donation from {donor_name}?")
        if confirm:
            global blood_donations
            blood_donations = [bd for bd in blood_donations if bd["id"] != blood_donation_id]
            self.clear_blood_donation_fields()
            self.refresh_blood_donations()
            self.save_data()
            self.update_status(f"Blood donation from '{donor_name}' deleted successfully.")
    
    # Search functions
    def search_members(self):
        query = self.member_search_entry.get().lower()
        if not query:
            self.refresh_members()
            return
        
        filtered = []
        for member in members:
            if (query in member["name"].lower() or 
                query in member["email"].lower() or 
                query in member["phone"].lower() or 
                query in member["address"].lower()):
                filtered.append(member)
        
        # Update treeview
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
        
        for member in filtered:
            self.member_tree.insert("", "end", values=(
                member["id"],
                member["name"],
                member["email"],
                member["phone"],
                member["address"]
            ))
    
    def search_events(self):
        query = self.event_search_entry.get().lower()
        if not query:
            self.refresh_events()
            return
        
        filtered = []
        for event in events:
            if (query in event["name"].lower() or 
                query in event["date"].lower() or 
                query in event["location"].lower() or 
                query in (event["description"] or "").lower()):
                filtered.append(event)
        
        # Update treeview
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        
        for event in filtered:
            self.event_tree.insert("", "end", values=(
                event["id"],
                event["name"],
                event["date"],
                event["location"],
                event["description"]
            ))
    
    def search_donations(self):
        query = self.donation_search_entry.get().lower()
        if not query:
            self.refresh_donations()
            return
        
        filtered = []
        for donation in donations:
            if (query in donation["donor_name"].lower() or 
                query in str(donation["amount"]).lower() or 
                query in donation["date"].lower()):
                filtered.append(donation)
        
        # Update treeview
        for item in self.donation_tree.get_children():
            self.donation_tree.delete(item)
        
        total = 0
        for donation in filtered:
            self.donation_tree.insert("", "end", values=(
                donation["id"],
                donation["donor_name"],
                f"${donation['amount']:.2f}",
                donation["date"]
            ))
            total += donation["amount"]
        
        # Update total
        self.total_donations_var.set(f"Total Donations: ${total:.2f}")
    
    def search_blood_donations(self):
        query = self.blood_donation_search_entry.get().lower()
        if not query:
            self.refresh_blood_donations()
            return
        
        filtered = []
        for bd in blood_donations:
            if (query in bd["donor_name"].lower() or 
                query in bd["blood_group"].lower() or 
                query in bd["donation_date"].lower()):
                filtered.append(bd)
        
        # Update treeview
        for item in self.blood_donation_tree.get_children():
            self.blood_donation_tree.delete(item)
        
        for bd in filtered:
            self.blood_donation_tree.insert("", "end", values=(
                bd["id"],
                bd["donor_name"],
                bd["blood_group"],
                bd["donation_date"]
            ))
        
        # Update total
        self.total_blood_donations_var.set(f"Total Blood Donations: {len(filtered)}")
    
    # Clear search functions
    def clear_member_search(self):
        self.member_search_entry.delete(0, "end")
        self.refresh_members()
    
    def clear_event_search(self):
        self.event_search_entry.delete(0, "end")
        self.refresh_events()
    
    def clear_donation_search(self):
        self.donation_search_entry.delete(0, "end")
        self.refresh_donations()
    
    def clear_blood_donation_search(self):
        self.blood_donation_search_entry.delete(0, "end")
        self.refresh_blood_donations()
    
    # Clear entry fields functions
    def clear_member_fields(self):
        for entry in self.member_entries.values():
            entry.delete(0, "end")
    
    def clear_event_fields(self):
        for entry in self.event_entries.values():
            entry.delete(0, "end")
    
    def clear_donation_fields(self):
        for entry in self.donation_entries.values():
            entry.delete(0, "end")
    
    def clear_blood_donation_fields(self):
        for entry in self.blood_donation_entries.values():
            entry.delete(0, "end")
    
    # Selection handlers
    def on_member_select(self, event):
        selected_item = self.member_tree.selection()
        if not selected_item:
            return
        
        item = self.member_tree.item(selected_item)
        member_id = item["values"][0]
        
        for member in members:
            if member["id"] == member_id:
                self.member_entries["name"].delete(0, "end")
                self.member_entries["name"].insert(0, member["name"])
                self.member_entries["email"].delete(0, "end")
                self.member_entries["email"].insert(0, member["email"])
                self.member_entries["phone"].delete(0, "end")
                self.member_entries["phone"].insert(0, member["phone"])
                self.member_entries["address"].delete(0, "end")
                self.member_entries["address"].insert(0, member["address"])
                self.member_entries["password"].delete(0, "end")
                self.member_entries["password"].insert(0, member["password"])
                break
    
    def on_event_select(self, event):
        selected_item = self.event_tree.selection()
        if not selected_item:
            return
        
        item = self.event_tree.item(selected_item)
        event_id = item["values"][0]
        
        for event in events:
            if event["id"] == event_id:
                self.event_entries["name"].delete(0, "end")
                self.event_entries["name"].insert(0, event["name"])
                self.event_entries["date"].delete(0, "end")
                self.event_entries["date"].insert(0, event["date"])
                self.event_entries["location"].delete(0, "end")
                self.event_entries["location"].insert(0, event["location"])
                self.event_entries["description"].delete(0, "end")
                self.event_entries["description"].insert(0, event.get("description", ""))
                break
    
    def on_donation_select(self, event):
        selected_item = self.donation_tree.selection()
        if not selected_item:
            return
        
        item = self.donation_tree.item(selected_item)
        donation_id = item["values"][0]
        
        for donation in donations:
            if donation["id"] == donation_id:
                self.donation_entries["donor"].delete(0, "end")
                self.donation_entries["donor"].insert(0, donation["donor_name"])
                self.donation_entries["amount"].delete(0, "end")
                self.donation_entries["amount"].insert(0, str(donation["amount"]))
                self.donation_entries["date"].delete(0, "end")
                self.donation_entries["date"].insert(0, donation["date"])
                break
    
    def on_blood_donation_select(self, event):
        selected_item = self.blood_donation_tree.selection()
        if not selected_item:
            return
        
        item = self.blood_donation_tree.item(selected_item)
        blood_donation_id = item["values"][0]
        
        for bd in blood_donations:
            if bd["id"] == blood_donation_id:
                self.blood_donation_entries["donor"].delete(0, "end")
                self.blood_donation_entries["donor"].insert(0, bd["donor_name"])
                self.blood_donation_entries["blood"].delete(0, "end")
                self.blood_donation_entries["blood"].insert(0, bd["blood_group"])
                self.blood_donation_entries["donation"].delete(0, "end")
                self.blood_donation_entries["donation"].insert(0, bd["donation_date"])
                break
    
    # Refresh functions
    def refresh_members(self):
        # Clear treeview
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
        
        # Add members to treeview
        for member in members:
            self.member_tree.insert("", "end", values=(
                member["id"],
                member["name"],
                member["email"],
                member["phone"],
                member["address"]
            ))
    
    def refresh_events(self):
        # Clear treeview
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        
        # Add events to treeview
        for event in events:
            self.event_tree.insert("", "end", values=(
                event["id"],
                event["name"],
                event["date"],
                event["location"],
                event["description"]
            ))
    
    def refresh_donations(self):
        # Clear treeview
        for item in self.donation_tree.get_children():
            self.donation_tree.delete(item)
        
        # Add donations to treeview
        total = 0
        for donation in donations:
            self.donation_tree.insert("", "end", values=(
                donation["id"],
                donation["donor_name"],
                f"${donation['amount']:.2f}",
                donation["date"]
            ))
            total += donation["amount"]
        
        # Update total
        self.total_donations_var.set(f"Total Donations: ${total:.2f}")
    
    def refresh_blood_donations(self):
        # Clear treeview
        for item in self.blood_donation_tree.get_children():
            self.blood_donation_tree.delete(item)
        
        # Add blood donations to treeview
        for bd in blood_donations:
            self.blood_donation_tree.insert("", "end", values=(
                bd["id"],
                bd["donor_name"],
                bd["blood_group"],
                bd["donation_date"]
            ))
        
        # Update total
        self.total_blood_donations_var.set(f"Total Blood Donations: {len(blood_donations)}")

class LoginWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Login")
        self.window.geometry("400x300")
        
        # Center the window
        window_width = 400
        window_height = 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Title
        ctk.CTkLabel(self.window, text="Organization System", font=("Arial", 20, "bold")).pack(pady=20)
        
        # Login frame
        login_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        login_frame.pack(pady=20, padx=20, fill="both") 
        
        # Username
        ctk.CTkLabel(login_frame, text="Username:").pack(pady=(0, 5))
        self.username_entry = ctk.CTkEntry(login_frame)
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        # Password
        ctk.CTkLabel(login_frame, text="Password:").pack(pady=(0, 5))
        self.password_entry = ctk.CTkEntry(login_frame, show="*")
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Login button
        ctk.CTkButton(login_frame, text="Login", command=self.login).pack(fill="x")
        
        # Status label
        self.status_label = ctk.CTkLabel(self.window, text="", text_color="red")
        self.status_label.pack(pady=10)
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.login())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        self.window.mainloop()
    
    def login(self):
        username = self.username_entry.get().upper()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.configure(text="Username and password are required")
            return
        
        if username in users and users[username] == password:
            self.status_label.configure(text="Login successful!", text_color="green")
            self.window.after(1000, self.open_main_app)
        else:
            self.status_label.configure(text="Invalid username or password")
    
    def open_main_app(self):
        self.window.destroy()
        root = ctk.CTk()
        app = OrganizationApp(root)
        root.mainloop()

# Start with login window
if __name__ == "__main__":
    LoginWindow()