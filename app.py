import tkinter as tk
from tkinter import messagebox, ttk, font
from datetime import datetime
import json
import os
import tempfile
import webbrowser
from ttkthemes import ThemedTk  # New library for better themes

# Constants
PRISE_EN_CHARGE = 3.70
INVOICE_FILE = "invoices.json"

# Color scheme
PRIMARY_COLOR = "#3498db"
SECONDARY_COLOR = "#2ecc71"
ACCENT_COLOR = "#e74c3c"
BG_COLOR = "#f5f5f5"
TEXT_COLOR = "#2c3e50"
HIGHLIGHT_COLOR = "#f39c12"

class TaxiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Taxi 123 - Gestion des factures")
        self.root.geometry("1000x630")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(800, 580)
        
        # Set up custom fonts
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=9)
        self.small_font = font.Font(family="Segoe UI", size=8)
        self.total_font = font.Font(family="Segoe UI", size=14, weight="bold")
        
        self.data = []
        self.load_data()
        
        # Add variables for help window and tooltip
        self.help_window = None
        self.tooltip = None
        
        self.build_ui()
        
        # Set up app icon
        try:
            self.root.iconbitmap("taxi_icon.ico")
        except:
            pass

    def validate_time(self, value):
        if value == "": return True
        try:
            val = int(value)
            return 0 <= val <= 23 if len(value) <= 2 else False
        except ValueError:
            return False

    def validate_minutes(self, value):
        if value == "": return True
        try:
            val = int(value)
            return 0 <= val <= 59 if len(value) <= 2 else False
        except ValueError:
            return False

    def build_ui(self):
        # Main container with reduced padding
        container = ttk.Frame(self.root, padding="5")
        container.pack(fill="both", expand=True)
        
        # Configure custom button styles
        style = ttk.Style()
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=self.normal_font)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TButton", font=self.normal_font)
        style.configure("TEntry", font=self.normal_font)
        style.configure("Header.TLabel", font=self.subtitle_font)
        style.configure("Total.TLabel", font=self.total_font)
        
        # Create main panels with better spacing
        main_frame = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Left panel (form)
        left_frame = ttk.Frame(main_frame, padding="5")
        left_frame.pack(side="left", fill="both", expand=True)
        
        # Right panel (invoice history)
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.pack(side="right", fill="both", expand=True)
        
        main_frame.add(left_frame, weight=60)
        main_frame.add(right_frame, weight=40)

        # Form variables
        self.nom_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.depart_hour = tk.StringVar(value="00")
        self.depart_minute = tk.StringVar(value="00")
        self.arrivee_hour = tk.StringVar(value="00")
        self.arrivee_minute = tk.StringVar(value="00")
        self.tarif_vars = [tk.StringVar(value="0") for _ in range(4)]
        self.resa_var = tk.IntVar(value=0)
        self.add_to_total_var = tk.StringVar(value="0")
        self.total_var = tk.StringVar(value="0.00")
        self.subtotal_var = tk.StringVar(value="0.00")

        # Left panel - Form section
        form_title = ttk.Label(left_frame, text="FACTURE TAXI", font=self.title_font, foreground=PRIMARY_COLOR)
        form_title.pack(pady=(0, 8))

        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill="both", expand=True)
        
        client_frame = ttk.LabelFrame(form_frame, text="Information Client", padding=5)
        client_frame.pack(fill="x", pady=3)
        
        ttk.Label(client_frame, text="Nom du client:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(client_frame, textvariable=self.nom_var, width=30).grid(row=0, column=1, sticky="we", pady=2, padx=5)
        
        ttk.Label(client_frame, text="Date:").grid(row=1, column=0, sticky="w", pady=2)
        date_entry = ttk.Entry(client_frame, textvariable=self.date_var, width=15)
        date_entry.grid(row=1, column=1, sticky="w", pady=2, padx=5)
        
        time_frame = ttk.LabelFrame(form_frame, text="Heure de course", padding=5)
        time_frame.pack(fill="x", pady=3)
        
        vcmd_hour = (self.root.register(self.validate_time), '%P')
        vcmd_min = (self.root.register(self.validate_minutes), '%P')
        
        ttk.Label(time_frame, text="Départ:").grid(row=0, column=0, sticky="w", pady=2)
        time_departure_frame = ttk.Frame(time_frame)
        time_departure_frame.grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Spinbox(time_departure_frame, from_=0, to=23, width=5, 
                    format="%02.0f", textvariable=self.depart_hour,
                    validate='all', validatecommand=vcmd_hour).pack(side="left")
        
        ttk.Label(time_departure_frame, text=":").pack(side="left", padx=2)
        
        ttk.Spinbox(time_departure_frame, from_=0, to=59, width=5,
                    format="%02.0f", textvariable=self.depart_minute,
                    validate='all', validatecommand=vcmd_min).pack(side="left")
        
        ttk.Label(time_frame, text="Arrivée:").grid(row=1, column=0, sticky="w", pady=2)
        time_arrival_frame = ttk.Frame(time_frame)
        time_arrival_frame.grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Spinbox(time_arrival_frame, from_=0, to=23, width=5,
                    format="%02.0f", textvariable=self.arrivee_hour,
                    validate='all', validatecommand=vcmd_hour).pack(side="left")
        
        ttk.Label(time_arrival_frame, text=":").pack(side="left", padx=2)
        
        ttk.Spinbox(time_arrival_frame, from_=0, to=59, width=5,
                    format="%02.0f", textvariable=self.arrivee_minute,
                    validate='all', validatecommand=vcmd_min).pack(side="left")
        
        tariff_frame = ttk.LabelFrame(form_frame, text="Tarifs", padding=5)
        tariff_frame.pack(fill="x", pady=3)
        
        tariff_labels = ["Tarif A Km", "Tarif B Km", "Tarif C Km", "Tarif D Km"]
        for i, label in enumerate(tariff_labels):
            row, col = divmod(i, 2)
            ttk.Label(tariff_frame, text=label).grid(row=row, column=col*2, sticky="w", pady=2, padx=(5 if col else 0, 0))
            ttk.Entry(tariff_frame, textvariable=self.tarif_vars[i], width=8).grid(row=row, column=col*2+1, pady=2, padx=5)
        
        resa_frame = ttk.LabelFrame(form_frame, text="RESA", padding=5)
        resa_frame.pack(fill="x", pady=3)
        
        for i, val in enumerate([4, 7, 0]):
            ttk.Radiobutton(resa_frame, text=str(val), variable=self.resa_var, value=val).grid(row=0, column=i, padx=15)
        
        additional_frame = ttk.LabelFrame(form_frame, text="Suppléments", padding=5)
        additional_frame.pack(fill="x", pady=3)
        
        ttk.Label(additional_frame, text="Ajouter au total:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(additional_frame, textvariable=self.add_to_total_var, width=8).grid(row=0, column=1, sticky="w", pady=2, padx=5)
        
        total_frame = ttk.Frame(form_frame, padding=5)
        total_frame.pack(fill="x", pady=3)
        
        ttk.Label(total_frame, text="Sous-total:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(total_frame, textvariable=self.subtotal_var).grid(row=0, column=1, sticky="e", pady=2)
        ttk.Label(total_frame, text="MAD").grid(row=0, column=2, sticky="w", pady=2, padx=(5, 0))
        
        ttk.Label(total_frame, text="Prise en charge:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(total_frame, text=f"{PRISE_EN_CHARGE:.2f}").grid(row=1, column=1, sticky="e", pady=2)
        ttk.Label(total_frame, text="MAD").grid(row=1, column=2, sticky="w", pady=2, padx=(5, 0))
        
        ttk.Separator(total_frame, orient="horizontal").grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(total_frame, text="TOTAL:", font=self.subtitle_font).grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(total_frame, textvariable=self.total_var, font=self.total_font, foreground=PRIMARY_COLOR).grid(row=3, column=1, sticky="e", pady=2)
        ttk.Label(total_frame, text="MAD", font=self.subtitle_font).grid(row=3, column=2, sticky="w", pady=2, padx=(5, 0))
        
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", pady=5)
        
        reset_btn = tk.Button(
            button_frame, 
            text="Réinitialiser", 
            command=self.reset_form,
            bg=ACCENT_COLOR,
            fg="white",
            font=self.normal_font,
            relief=tk.RAISED,
            borderwidth=2,
            padx=5
        )
        reset_btn.pack(side="left", padx=2)
        
        calc_btn = tk.Button(
            button_frame, 
            text="Calculer", 
            command=self.calculate_total,
            bg=PRIMARY_COLOR,
            fg="white",
            font=self.normal_font,
            relief=tk.RAISED,
            borderwidth=2,
            padx=5
        )
        calc_btn.pack(side="left", padx=2)
        
        save_btn = tk.Button(
            button_frame, 
            text="Enregistrer", 
            command=self.save_invoice,
            bg=PRIMARY_COLOR,
            fg="white",
            font=self.normal_font,
            relief=tk.RAISED,
            borderwidth=2,
            padx=5
        )
        save_btn.pack(side="left", padx=2)
        
        print_btn = tk.Button(
            button_frame, 
            text="Enreg. et imprimer", 
            command=lambda: self.save_invoice(print_it=True),
            bg=SECONDARY_COLOR,
            fg="white",
            font=self.normal_font,
            relief=tk.RAISED,
            borderwidth=2,
            padx=5
        )
        print_btn.pack(side="right", padx=2)
        
        # Right panel - Invoice history
        title_frame = ttk.Frame(right_frame)
        title_frame.pack(fill="x", pady=(0, 8))
        
        history_title = ttk.Label(title_frame, text="HISTORIQUE DES FACTURES", font=self.title_font, foreground=PRIMARY_COLOR)
        history_title.pack(side="left")
        
        help_button = ttk.Button(title_frame, text="?", width=2, command=self.show_help)
        help_button.pack(side="right")
        
        help_button.bind("<Enter>", self.show_tooltip)
        help_button.bind("<Leave>", self.hide_tooltip)
        
        self.title_frame = title_frame
        self.help_button = help_button
        
        columns = ("date", "client", "total")
        self.invoice_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=13)
        
        self.invoice_tree.heading("date", text="Date")
        self.invoice_tree.heading("client", text="Client")
        self.invoice_tree.heading("total", text="Total (MAD)")
        
        self.invoice_tree.column("date", width=90)
        self.invoice_tree.column("client", width=140)
        self.invoice_tree.column("total", width=90, anchor="e")
        
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.invoice_tree.pack(fill="both", expand=True, pady=3)
        
        self.invoice_tree.bind("<<TreeviewSelect>>", self.on_select_invoice)
        
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill="x", pady=5)
        
        download_btn = tk.Button(
            action_frame, 
            text="Télécharger", 
            command=self.download_invoice,
            bg=PRIMARY_COLOR,
            fg="white",
            font=self.normal_font,
            relief=tk.RAISED,
            borderwidth=2,
            padx=5
        )
        download_btn.pack(side="left", padx=2)
        
        print_select_btn = tk.Button(
            action_frame, 
            text="Imprimer", 
            command=lambda: self.print_selected_invoice(),
            bg=SECONDARY_COLOR,
            fg="white",
            font=self.normal_font,
            relief=tk.RAISED,
            borderwidth=2,
            padx=5
        )
        print_select_btn.pack(side="left", padx=2)
        
        delete_btn = tk.Button(
            action_frame, 
            text="Effacer", 
            command=self.delete_invoice,
            bg=ACCENT_COLOR,
            fg="white",
            font=self.normal_font,
            relief=tk.RAISED,
            borderwidth=2,
            padx=5
        )
        delete_btn.pack(side="right", padx=2)
        
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.StringVar(value="Prêt")
        ttk.Label(status_bar, textvariable=self.status_text, font=self.small_font).pack(side=tk.LEFT, padx=3, pady=1)
        
        for button in [reset_btn, calc_btn, save_btn, print_btn, download_btn, print_select_btn, delete_btn]:
            self._add_button_hover(button)
        
        self.refresh_invoice_list()

    def _add_button_hover(self, button):
        original_color = button["bg"]
        
        def on_enter(e):
            r, g, b = button.winfo_rgb(original_color)
            darker = f'#{int(r*0.8/256):02x}{int(g*0.8/256):02x}{int(b*0.8/256):02x}'
            button["bg"] = darker
            
        def on_leave(e):
            button["bg"] = original_color
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def calculate_total(self):
        try:
            values = [float(var.get()) for var in self.tarif_vars]
            resa_val = self.resa_var.get()  # Get the RESA value
            subtotal = sum(values) + resa_val  # Include RESA in the subtotal
            add_val = float(self.add_to_total_var.get())
            total = subtotal + PRISE_EN_CHARGE + add_val
            self.subtotal_var.set(f"{subtotal:.2f}")
            self.total_var.set(f"{total:.2f}")
            self.status_text.set("Total calculé avec succès")
        except ValueError:
            messagebox.showerror("Erreur", "Vérifiez les champs numériques")
            self.status_text.set("Erreur de calcul")

    def reset_form(self):
        self.nom_var.set("")
        self.date_var.set(datetime.now().strftime("%d/%m/%Y"))
        self.depart_hour.set("00")
        self.depart_minute.set("00")
        self.arrivee_hour.set("00")
        self.arrivee_minute.set("00")
        for tarif_var in self.tarif_vars:
            tarif_var.set("0")
        self.resa_var.set(0)
        self.add_to_total_var.set("0")
        self.total_var.set("0.00")
        self.subtotal_var.set("0.00")
        self.status_text.set("Formulaire réinitialisé")

    def save_invoice(self, print_it=False):
        if not self.nom_var.get().strip():
            messagebox.showwarning("Attention", "Veuillez entrer le nom du client")
            return
            
        self.calculate_total()
        departure_time = f"{self.depart_hour.get()}:{self.depart_minute.get()}"
        arrival_time = f"{self.arrivee_hour.get()}:{self.arrivee_minute.get()}"
        tarifs = [float(var.get()) for var in self.tarif_vars]  # Collect tarifs values
        invoice = {
            "date": self.date_var.get(),
            "name": self.nom_var.get(),
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "total": float(self.total_var.get()),
            "tarifs": tarifs  # Add tarifs to the invoice
        }
        self.data.append(invoice)
        self.save_data()
        self.refresh_invoice_list()
        
        if print_it:
            self.print_invoice(invoice)
            self.status_text.set(f"Facture pour {invoice['name']} enregistrée et imprimée")
        else:
            self.status_text.set(f"Facture pour {invoice['name']} enregistrée")

    def refresh_invoice_list(self):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        for invoice in self.data:
            self.invoice_tree.insert("", "end", values=(
                invoice['date'],
                invoice['name'],
                f"{invoice['total']:.2f}"
            ))
        
        self.status_text.set(f"{len(self.data)} factures au total")

    def on_select_invoice(self, event):
        selected_items = self.invoice_tree.selection()
        if not selected_items:
            return
            
        item = selected_items[0]
        values = self.invoice_tree.item(item, "values")
        
        for invoice in self.data:
            if (invoice['date'] == values[0] and 
                invoice['name'] == values[1] and 
                f"{invoice['total']:.2f}" == values[2]):
                self.selected_invoice = invoice
                self.status_text.set(f"Facture sélectionnée: {invoice['name']}")
                break

    def print_selected_invoice(self):
        if hasattr(self, 'selected_invoice'):
            self.print_invoice(self.selected_invoice)
        else:
            messagebox.showinfo("Information", "Veuillez sélectionner une facture d'abord")

    def delete_invoice(self):
        if hasattr(self, 'selected_invoice'):
            confirm = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer la facture de {self.selected_invoice['name']}?")
            if confirm:
                self.data.remove(self.selected_invoice)
                self.save_data()
                self.refresh_invoice_list()
                self.status_text.set(f"Facture supprimée")
                delattr(self, 'selected_invoice')
        else:
            messagebox.showinfo("Information", "Veuillez sélectionner une facture d'abord")

    def print_invoice(self, invoice):
        content = f"""
        BENATSOU YAZID

Date course:        {invoice['date']:<20}

Heure départ:            {invoice['departure_time']:<20}
Heure d'arrivée:         {invoice['arrival_time']:<20}

******************************
Tarif(s) appliqué(s)

Tarif A (km):   {invoice['tarifs'][0]:>10.2f} MAD
Tarif B (km):   {invoice['tarifs'][1]:>10.2f} MAD
Tarif C (km):   {invoice['tarifs'][2]:>10.2f} MAD
Tarif D (km):   {invoice['tarifs'][3]:>10.2f} MAD

RESA:           {float(self.resa_var.get()):>10.2f} MAD
Prise en charge:{PRISE_EN_CHARGE:>10.2f} MAD
Ajouter au total:{float(self.add_to_total_var.get()):>9.2f} MAD

Total TTC:      {invoice['total']:>10.2f} MAD
TVA (10%):      {invoice['total']*0.10:>10.2f} MAD
Sous-total HT:  {invoice['total']*0.90:>10.2f} MAD
******************************
Nom du client:          {invoice['name']:<20}
******************************

    Exemplaire chauffeur
"""
        file_path = os.path.join(tempfile.gettempdir(), "ticket.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        os.startfile(file_path, "print")
        self.status_text.set(f"Impression de la facture en cours...")

    def download_invoice(self):
        if hasattr(self, 'selected_invoice'):
            content = f"""
        BENATSOU YAZID

Date course:        {self.selected_invoice['date']:<20}

Heure départ:            {self.selected_invoice['departure_time']:<20}
Heure d'arrivée:         {self.selected_invoice['arrival_time']:<20}

******************************
Tarif(s) appliqué(s)

Tarif A (km):   {self.selected_invoice['tarifs'][0]:>10.2f} MAD
Tarif B (km):   {self.selected_invoice['tarifs'][1]:>10.2f} MAD
Tarif C (km):   {self.selected_invoice['tarifs'][2]:>10.2f} MAD
Tarif D (km):   {self.selected_invoice['tarifs'][3]:>10.2f} MAD

RESA:           {float(self.resa_var.get()):>10.2f} MAD
Prise en charge:{PRISE_EN_CHARGE:>10.2f} MAD
Ajouter au total:{float(self.add_to_total_var.get()):>9.2f} MAD

Total TTC:      {self.selected_invoice['total']:>10.2f} MAD
TVA (10%):      {self.selected_invoice['total']*0.10:>10.2f} MAD
Sous-total HT:  {self.selected_invoice['total']*0.90:>10.2f} MAD
******************************
Nom du client:          {self.selected_invoice['name']:<20}
******************************

    Exemplaire chauffeur
"""
            path = os.path.join(os.getcwd(), f"facture_{self.selected_invoice['name'].replace(' ', '_')}.txt")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            webbrowser.open(path)
            self.status_text.set(f"Facture téléchargée: {path}")
        else:
            messagebox.showinfo("Information", "Veuillez sélectionner une facture d'abord")

    def save_data(self):
        with open(INVOICE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def load_data(self):
        if os.path.exists(INVOICE_FILE):
            with open(INVOICE_FILE, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def show_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = tk.Label(
            self.title_frame,
            text="Afficher l'aide",
            background="yellow",
            relief="solid",
            borderwidth=1
        )
        self.tooltip.place(
            x=self.help_button.winfo_x(),
            y=self.help_button.winfo_y() + self.help_button.winfo_height() + 5
        )

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def show_help(self):
        if self.help_window and self.help_window.winfo_exists():
            self.help_window.lift()
            self.help_window.focus_force()
        else:
            self.help_window = tk.Toplevel(self.root)
            self.help_window.title("Aide - Taxi 123")
            self.help_window.geometry("450x350")
            self.help_window.transient(self.root)

            header_frame = tk.Frame(self.help_window, pady=10)
            header_frame.pack(fill="x")
            header_label = tk.Label(
                header_frame, 
                text="Aide - Instructions d'utilisation", 
                font=self.title_font
            )
            header_label.pack()

            content_frame = tk.Frame(self.help_window, padx=10, pady=10)
            content_frame.pack(fill="both", expand=True)

            instructions = tk.Text(
                content_frame, 
                wrap="word", 
                height=15, 
                width=50, 
                font=self.normal_font, 
                relief="flat"
            )
            instructions.insert("end", "Instructions d'utilisation\n", "header")
            instructions.insert("end", "\nCréer une facture :\n", "subheader")
            instructions.insert("end", "1. Remplissez les informations du client (nom et date).\n")
            instructions.insert("end", "2. Entrez les heures de départ et d'arrivée.\n")
            instructions.insert("end", "3. Ajoutez les tarifs (A, B, C, D) en kilomètres.\n")
            instructions.insert("end", "4. Sélectionnez une option RESA (4, 7, ou 0).\n")
            instructions.insert("end", "5. Ajoutez un supplément si nécessaire.\n")
            instructions.insert("end", "6. Cliquez sur 'Calculer' pour voir le total.\n")
            instructions.insert("end", "7. Cliquez sur 'Enregistrer' pour sauvegarder ou 'Enreg. et imprimer' pour imprimer.\n")
            instructions.insert("end", "\nHistorique des factures :\n", "subheader")
            instructions.insert("end", "- Sélectionnez une facture dans la liste.\n")
            instructions.insert("end", "- 'Télécharger' pour sauvegarder en fichier texte.\n")
            instructions.insert("end", "- 'Imprimer' pour imprimer la facture sélectionnée.\n")
            instructions.insert("end", "- 'Effacer' pour supprimer la facture sélectionnée.\n")

            instructions.tag_configure("header", font=self.title_font)
            instructions.tag_configure("subheader", font=self.subtitle_font)
            instructions.config(state="disabled")

            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=instructions.yview)
            instructions.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            instructions.pack(side="left", fill="both", expand=True)

            footer_frame = tk.Frame(self.help_window, pady=10)
            footer_frame.pack(fill="x")
            close_button = tk.Button(
                footer_frame, 
                text="Fermer", 
                command=self.on_help_close, 
                bg=ACCENT_COLOR, 
                fg="white", 
                font=self.normal_font, 
                relief="flat", 
                padx=10, 
                pady=5
            )
            close_button.pack()

            self.help_window.protocol("WM_DELETE_WINDOW", self.on_help_close)

    def on_help_close(self):
        self.help_window.destroy()
        self.help_window = None

if __name__ == '__main__':
    root = ThemedTk(theme="arc")  # Using a modern theme from ttkthemes
    app = TaxiApp(root)
    root.mainloop()