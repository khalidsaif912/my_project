import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from decimal import Decimal
import datetime
import json
import os
from tkinter.font import Font

class ShipmentWeightSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("Shipment Weight Splitter")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f7fa")
        
        # إعداد نظام الألوان
        self.colors = {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "dark": "#2c3e50",
            "light": "#ecf0f1",
            "card": "#ffffff",
            "header": "#34495e"
        }
        
        # إعداد الخطوط
        self.title_font = Font(family="Segoe UI", size=14, weight="bold")
        self.subtitle_font = Font(family="Segoe UI", size=12, weight="bold")
        self.body_font = Font(family="Segoe UI", size=10)
        
        # تهيئة متغيرات التطبيق
        self.current_awb = None
        self.batches = []
        self.parts = []
        self.shipments = {}
        
        # إنشاء واجهة المستخدم
        self.create_widgets()
        self.create_menu()
        
        # تحميل البيانات المحفوظة إن وجدت
        self.load_data()
        
    def create_menu(self):
        # إنشاء شريط القوائم
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # قائمة ملف
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Shipment", command=self.add_shipment)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # قائمة مساعدة
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_widgets(self):
        # إنشاء إطار رئيسي
        main_frame = tk.Frame(self.root, bg=self.colors["light"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # قسم العنوان
        header_frame = tk.Frame(main_frame, bg=self.colors["header"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame, 
            text="Shipment Weight Splitter", 
            font=self.title_font,
            bg=self.colors["header"],
            fg="white",
            padx=20,
            pady=15
        ).pack(side=tk.LEFT)
        
        # إنشاء تبويبات الشحنات
        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # إطار المعلومات الأساسية
        info_frame = tk.Frame(main_frame, bg=self.colors["card"], bd=1, relief=tk.GROOVE)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # بطاقة معلومات الشحنة
        shipment_card = tk.LabelFrame(
            info_frame, 
            text="Shipment Information",
            font=self.subtitle_font,
            bg=self.colors["card"],
            padx=15,
            pady=10
        )
        shipment_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            shipment_card, 
            text="AWB Number:", 
            bg=self.colors["card"],
            font=self.body_font
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.awb_var = tk.StringVar()
        awb_entry = tk.Entry(
            shipment_card, 
            textvariable=self.awb_var,
            font=self.body_font,
            width=20
        )
        awb_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(
            shipment_card, 
            text="Total Quantity:", 
            bg=self.colors["card"],
            font=self.body_font
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.quantity_var = tk.IntVar(value=0)
        quantity_entry = tk.Entry(
            shipment_card, 
            textvariable=self.quantity_var,
            font=self.body_font,
            width=10
        )
        quantity_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(
            shipment_card, 
            text="Total Weight (kg):", 
            bg=self.colors["card"],
            font=self.body_font
        ).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.weight_var = tk.DoubleVar(value=0.0)
        weight_entry = tk.Entry(
            shipment_card, 
            textvariable=self.weight_var,
            font=self.body_font,
            width=10
        )
        weight_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # أزرار التحكم
        button_frame = tk.Frame(info_frame, bg=self.colors["card"])
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Button(
            button_frame,
            text="Add Batch",
            bg=self.colors["secondary"],
            fg="white",
            font=self.body_font,
            command=self.add_batch,
            width=12
        ).pack(pady=5, fill=tk.X)
        
        tk.Button(
            button_frame,
            text="Add Part",
            bg=self.colors["primary"],
            fg="white",
            font=self.body_font,
            command=self.add_part,
            width=12
        ).pack(pady=5, fill=tk.X)
        
        tk.Button(
            button_frame,
            text="Save Shipment",
            bg=self.colors["warning"],
            fg="white",
            font=self.body_font,
            command=self.save_shipment,
            width=12
        ).pack(pady=5, fill=tk.X)
        
        # إطار الدفعات والأجزاء
        data_frame = tk.Frame(main_frame)
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        # قسم الدفعات
        batch_frame = tk.LabelFrame(
            data_frame,
            text="Batches",
            font=self.subtitle_font,
            bg=self.colors["card"],
            padx=15,
            pady=10
        )
        batch_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # شجرة الدفعات
        self.batch_tree = ttk.Treeview(
            batch_frame,
            columns=("id", "quantity", "weight", "time"),
            show="headings",
            height=10
        )
        self.batch_tree.heading("id", text="Batch ID")
        self.batch_tree.heading("quantity", text="Quantity")
        self.batch_tree.heading("weight", text="Weight (kg)")
        self.batch_tree.heading("time", text="Time")
        
        self.batch_tree.column("id", width=100)
        self.batch_tree.column("quantity", width=100)
        self.batch_tree.column("weight", width=100)
        self.batch_tree.column("time", width=150)
        
        self.batch_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # أزرار إدارة الدفعات
        batch_btn_frame = tk.Frame(batch_frame, bg=self.colors["card"])
        batch_btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            batch_btn_frame,
            text="Edit Batch",
            bg=self.colors["primary"],
            fg="white",
            font=self.body_font,
            command=self.edit_batch,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            batch_btn_frame,
            text="Delete Batch",
            bg=self.colors["danger"],
            fg="white",
            font=self.body_font,
            command=self.delete_batch,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # قسم الأجزاء
        part_frame = tk.LabelFrame(
            data_frame,
            text="Parts",
            font=self.subtitle_font,
            bg=self.colors["card"],
            padx=15,
            pady=10
        )
        part_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # شجرة الأجزاء
        self.part_tree = ttk.Treeview(
            part_frame,
            columns=("id", "batch_id", "weight", "source"),
            show="headings",
            height=10
        )
        self.part_tree.heading("id", text="Part ID")
        self.part_tree.heading("batch_id", text="Batch ID")
        self.part_tree.heading("weight", text="Weight (kg)")
        self.part_tree.heading("source", text="Source")
        
        self.part_tree.column("id", width=100)
        self.part_tree.column("batch_id", width=100)
        self.part_tree.column("weight", width=100)
        self.part_tree.column("source", width=150)
        
        self.part_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # أزرار إدارة الأجزاء
        part_btn_frame = tk.Frame(part_frame, bg=self.colors["card"])
        part_btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            part_btn_frame,
            text="Edit Part",
            bg=self.colors["primary"],
            fg="white",
            font=self.body_font,
            command=self.edit_part,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            part_btn_frame,
            text="Delete Part",
            bg=self.colors["danger"],
            fg="white",
            font=self.body_font,
            command=self.delete_part,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # شريط الحالة
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=self.colors["dark"],
            fg="white",
            font=self.body_font,
            padx=10
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # إضافة شحنة افتراضية للعرض
        self.add_shipment()
    
    def add_shipment(self):
        """إضافة شحنة جديدة"""
        awb = simpledialog.askstring("New Shipment", "Enter AWB Number:")
        if awb:
            self.current_awb = awb
            self.awb_var.set(awb)
            self.quantity_var.set(0)
            self.weight_var.set(0.0)
            self.batches = []
            self.parts = []
            self.update_batch_tree()
            self.update_part_tree()
            self.update_status(f"New shipment created: {awb}")
            
            # إضافة تبويب جديد
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=awb)
            self.tab_control.select(tab)
    
    def save_shipment(self):
        """حفظ بيانات الشحنة الحالية"""
        if not self.current_awb:
            messagebox.showerror("Error", "No active shipment to save!")
            return
        
        if not self.awb_var.get():
            messagebox.showerror("Error", "AWB number is required!")
            return
        
        self.shipments[self.current_awb] = {
            "awb": self.awb_var.get(),
            "quantity": self.quantity_var.get(),
            "weight": self.weight_var.get(),
            "batches": self.batches,
            "parts": self.parts
        }
        
        self.update_status(f"Shipment saved: {self.current_awb}")
        messagebox.showinfo("Success", "Shipment saved successfully!")
    
    def add_batch(self):
        """إضافة دفعة جديدة"""
        if not self.current_awb:
            messagebox.showerror("Error", "Please create or select a shipment first!")
            return
        
        batch_id = simpledialog.askstring("Add Batch", "Enter Batch ID:")
        if batch_id:
            quantity = simpledialog.askinteger("Add Batch", "Enter Quantity:")
            weight = simpledialog.askfloat("Add Batch", "Enter Weight (kg):")
            
            if quantity and weight:
                batch_data = {
                    "id": batch_id,
                    "quantity": quantity,
                    "weight": Decimal(str(weight)),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                self.batches.append(batch_data)
                self.update_batch_tree()
                self.update_totals()
                self.update_status(f"Batch added: {batch_id}")
    
    def edit_batch(self):
        """تعديل دفعة محددة"""
        selected = self.batch_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a batch to edit!")
            return
        
        item = self.batch_tree.item(selected[0])
        values = item['values']
        batch_id = values[0]
        
        # البحث عن الدفعة
        batch = next((b for b in self.batches if b["id"] == batch_id), None)
        if not batch:
            return
        
        # إنشاء نافذة التعديل
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Batch")
        edit_win.geometry("300x200")
        edit_win.resizable(False, False)
        
        tk.Label(edit_win, text="Batch ID:", font=self.body_font).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        id_entry = tk.Entry(edit_win, font=self.body_font)
        id_entry.insert(0, batch["id"])
        id_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        id_entry.config(state=tk.DISABLED)
        
        tk.Label(edit_win, text="Quantity:", font=self.body_font).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        qty_var = tk.IntVar(value=batch["quantity"])
        qty_entry = tk.Entry(edit_win, textvariable=qty_var, font=self.body_font)
        qty_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(edit_win, text="Weight (kg):", font=self.body_font).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        weight_var = tk.DoubleVar(value=float(batch["weight"]))
        weight_entry = tk.Entry(edit_win, textvariable=weight_var, font=self.body_font)
        weight_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        
        def save_changes():
            batch["quantity"] = qty_var.get()
            batch["weight"] = Decimal(str(weight_var.get()))
            batch["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.update_batch_tree()
            self.update_totals()
            edit_win.destroy()
            self.update_status(f"Batch updated: {batch_id}")
        
        tk.Button(
            edit_win,
            text="Save Changes",
            bg=self.colors["primary"],
            fg="white",
            font=self.body_font,
            command=save_changes
        ).grid(row=3, column=0, columnspan=2, pady=20)
    
    def delete_batch(self):
        """حذف دفعة محددة"""
        selected = self.batch_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a batch to delete!")
            return
        
        item = self.batch_tree.item(selected[0])
        values = item['values']
        batch_id = values[0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete batch {batch_id}?"):
            self.batches = [b for b in self.batches if b["id"] != batch_id]
            self.update_batch_tree()
            self.update_totals()
            self.update_status(f"Batch deleted: {batch_id}")
    
    def add_part(self):
        """إضافة جزء جديد"""
        if not self.current_awb:
            messagebox.showerror("Error", "Please create or select a shipment first!")
            return
        
        if not self.batches:
            messagebox.showwarning("Warning", "Please add batches first!")
            return
        
        part_id = simpledialog.askstring("Add Part", "Enter Part ID:")
        if part_id:
            weight = simpledialog.askfloat("Add Part", "Enter Weight (kg):")
            
            # اختيار الدفعة المصدر
            source_win = tk.Toplevel(self.root)
            source_win.title("Select Source Batch")
            source_win.geometry("300x150")
            source_win.resizable(False, False)
            
            tk.Label(source_win, text="Select Source Batch:", font=self.body_font).pack(pady=10)
            
            batch_var = tk.StringVar()
            batch_dropdown = ttk.Combobox(
                source_win,
                textvariable=batch_var,
                values=[b["id"] for b in self.batches],
                state="readonly"
            )
            batch_dropdown.pack(pady=5)
            batch_dropdown.current(0)
            
            def save_part():
                if weight and batch_var.get():
                    part_data = {
                        "id": part_id,
                        "batch_id": batch_var.get(),
                        "weight": Decimal(str(weight)),
                        "source": f"Batch: {batch_var.get()}"
                    }
                    
                    self.parts.append(part_data)
                    self.update_part_tree()
                    self.update_totals()
                    source_win.destroy()
                    self.update_status(f"Part added: {part_id}")
            
            tk.Button(
                source_win,
                text="Add Part",
                bg=self.colors["primary"],
                fg="white",
                font=self.body_font,
                command=save_part
            ).pack(pady=10)
    
    def edit_part(self):
        """تعديل جزء محدد"""
        selected = self.part_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a part to edit!")
            return
        
        item = self.part_tree.item(selected[0])
        values = item['values']
        part_id = values[0]
        
        # البحث عن الجزء
        part = next((p for p in self.parts if p["id"] == part_id), None)
        if not part:
            return
        
        # إنشاء نافذة التعديل
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Part")
        edit_win.geometry("300x200")
        edit_win.resizable(False, False)
        
        tk.Label(edit_win, text="Part ID:", font=self.body_font).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        id_entry = tk.Entry(edit_win, font=self.body_font)
        id_entry.insert(0, part["id"])
        id_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        id_entry.config(state=tk.DISABLED)
        
        tk.Label(edit_win, text="Weight (kg):", font=self.body_font).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        weight_var = tk.DoubleVar(value=float(part["weight"]))
        weight_entry = tk.Entry(edit_win, textvariable=weight_var, font=self.body_font)
        weight_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(edit_win, text="Source Batch:", font=self.body_font).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        batch_var = tk.StringVar(value=part["batch_id"])
        batch_dropdown = ttk.Combobox(
            edit_win,
            textvariable=batch_var,
            values=[b["id"] for b in self.batches],
            state="readonly"
        )
        batch_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        
        def save_changes():
            part["weight"] = Decimal(str(weight_var.get()))
            part["batch_id"] = batch_var.get()
            part["source"] = f"Batch: {batch_var.get()}"
            self.update_part_tree()
            self.update_totals()
            edit_win.destroy()
            self.update_status(f"Part updated: {part_id}")
        
        tk.Button(
            edit_win,
            text="Save Changes",
            bg=self.colors["primary"],
            fg="white",
            font=self.body_font,
            command=save_changes
        ).grid(row=3, column=0, columnspan=2, pady=20)
    
    def delete_part(self):
        """حذف جزء محدد"""
        selected = self.part_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a part to delete!")
            return
        
        item = self.part_tree.item(selected[0])
        values = item['values']
        part_id = values[0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete part {part_id}?"):
            self.parts = [p for p in self.parts if p["id"] != part_id]
            self.update_part_tree()
            self.update_totals()
            self.update_status(f"Part deleted: {part_id}")
    
    def update_batch_tree(self):
        """تحديث شجرة الدفعات"""
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
        
        for batch in self.batches:
            self.batch_tree.insert("", "end", values=(
                batch["id"],
                batch["quantity"],
                float(batch["weight"]),
                batch["time"]
            ))
    
    def update_part_tree(self):
        """تحديث شجرة الأجزاء"""
        for item in self.part_tree.get_children():
            self.part_tree.delete(item)
        
        for part in self.parts:
            self.part_tree.insert("", "end", values=(
                part["id"],
                part["batch_id"],
                float(part["weight"]),
                part["source"]
            ))
    
    def update_totals(self):
        """تحديث الإجماليات"""
        total_quantity = sum(b["quantity"] for b in self.batches)
        total_weight = sum(float(b["weight"]) for b in self.batches)
        
        self.quantity_var.set(total_quantity)
        self.weight_var.set(round(total_weight, 2))
    
    def save_data(self):
        """حفظ البيانات في ملف"""
        data = {
            "shipments": self.shipments,
            "current_awb": self.current_awb
        }
        
        try:
            with open("shipment_data.json", "w") as f:
                json.dump(data, f, default=str, indent=2)
            self.update_status("Data saved successfully!")
            messagebox.showinfo("Success", "Data saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def load_data(self):
        """تحميل البيانات من ملف"""
        if not os.path.exists("shipment_data.json"):
            return
        
        try:
            with open("shipment_data.json", "r") as f:
                data = json.load(f)
            
            self.shipments = data.get("shipments", {})
            self.current_awb = data.get("current_awb")
            
            if self.current_awb and self.current_awb in self.shipments:
                shipment = self.shipments[self.current_awb]
                self.awb_var.set(shipment["awb"])
                self.quantity_var.set(shipment["quantity"])
                self.weight_var.set(shipment["weight"])
                self.batches = shipment["batches"]
                self.parts = shipment["parts"]
                
                # تحويل الأوزان إلى Decimal
                for batch in self.batches:
                    batch["weight"] = Decimal(str(batch["weight"]))
                
                for part in self.parts:
                    part["weight"] = Decimal(str(part["weight"]))
                
                self.update_batch_tree()
                self.update_part_tree()
                self.update_totals()
                self.update_status("Data loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def update_status(self, message):
        """تحديث شريط الحالة"""
        self.status_var.set(f"Status: {message}")
    
    def show_about(self):
        """عرض معلومات حول البرنامج"""
        about_text = (
            "Shipment Weight Splitter\n"
            "Version 1.0\n"
            "Created by: Khalid Al-Raqadi\n"
            "Date: August 2023\n\n"
            "A tool for managing and splitting air shipment weights"
        )
        messagebox.showinfo("About", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShipmentWeightSplitter(root)
    root.mainloop()