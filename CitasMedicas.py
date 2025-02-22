import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from PIL import Image, ImageTk
import sys
import os


class CitasMedicas:
    def __init__(self, window):
        self.window = window
        self.window.title("Citas Médicas")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        self.image = Image.open(resource_path("images/fondo.png"))
        self.bg_image = ImageTk.PhotoImage(self.image)
        self.bg_label = tk.Label(self.window, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        self.frame = tk.LabelFrame(self.window, text="Citas Médicas", bg="light blue")
        self.frame.pack(pady=20)

        self.label_user = tk.Label(self.frame, text="Usuario:", bg="light blue")
        self.label_user.grid(row=0, column=0, padx=5, pady=5)

        self.entry_user = tk.Entry(self.frame)
        self.entry_user.grid(row=0, column=1, padx=5, pady=5)

        self.label_pass = tk.Label(self.frame, text="Contraseña:", bg="light blue")
        self.label_pass.grid(row=1, column=0, padx=5, pady=5)

        self.entry_pass = tk.Entry(self.frame, show="*")
        self.entry_pass.grid(row=1, column=1, padx=5, pady=5)

        self.button_login = tk.Button(self.frame, text="Iniciar Sesión", command=self.login, bg="light green")
        self.button_login.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

        self.button_register = tk.Button(self.frame, text="Registrar Usuario", command=self.registrar_usuario, bg="light green")
        self.button_register.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

        self.create_db()
        self.add_admin_user()

    def create_db(self):
        self.conn = sqlite3.connect('citas_medicas.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS citas (
                                id INTEGER PRIMARY KEY,
                                nombre TEXT,
                                apellidos TEXT,
                                edad INTEGER,
                                telefono TEXT,
                                direccion TEXT,
                                fecha TEXT,
                                hora TEXT,
                                medico TEXT,
                                especialidad TEXT,
                                estado TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                                id INTEGER PRIMARY KEY,
                                nombres TEXT,
                                apellidos TEXT,
                                correo TEXT,
                                fecha_nacimiento TEXT,
                                usuario TEXT UNIQUE,
                                contrasena TEXT,
                                especialidad TEXT)''')
        self.conn.commit()

    def add_admin_user(self):
        try:
            self.cursor.execute("INSERT INTO usuarios (nombres, apellidos, correo, fecha_nacimiento, usuario, contrasena, especialidad) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                ("Admin", "Admin", "admin@example.com", "01/01/1970", "admin", "12345", "Administrador"))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # El usuario admin ya existe

    def login(self):
        usuario = self.entry_user.get()
        contrasena = self.entry_pass.get()
        self.cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contrasena=?", (usuario, contrasena))
        user = self.cursor.fetchone()
        if user:
            self.frame.destroy()
            self.menu(user)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def registrar_usuario(self):
        self.reg_window = tk.Toplevel(self.window)
        self.reg_window.title("Registrar Usuario")
        self.reg_window.geometry("400x400")
        self.reg_window.config(bg="light blue")

        self.reg_frame = tk.LabelFrame(self.reg_window, text="Registrar Usuario", bg="light blue")
        self.reg_frame.pack(pady=20)

        labels = ["Nombres", "Apellidos", "Correo", "Fecha de Nacimiento", "Usuario", "Contraseña", "Especialidad (opcional)"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.reg_frame, text=label + ":", bg="light blue").grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(self.reg_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = entry

        self.button_save = tk.Button(self.reg_frame, text="Guardar", command=self.guardar_usuario, bg="light green")
        self.button_save.grid(row=len(labels), column=0, columnspan=2, padx=5, pady=5, sticky="WE")

        self.button_back = tk.Button(self.reg_frame, text="Atrás", command=self.reg_window.destroy, bg="light green")
        self.button_back.grid(row=len(labels) + 1, column=0, padx=5, pady=5, sticky="WE")

        self.button_exit = tk.Button(self.reg_frame, text="Salir", command=self.window.quit, bg="light green")
        self.button_exit.grid(row=len(labels) + 1, column=1, padx=5, pady=5, sticky="WE")

    def guardar_usuario(self):
        datos = {label: entry.get() for label, entry in self.entries.items()}
        if all(datos.values()):
            try:
                self.cursor.execute("INSERT INTO usuarios (nombres, apellidos, correo, fecha_nacimiento, usuario, contrasena, especialidad) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (datos["Nombres"], datos["Apellidos"], datos["Correo"], datos["Fecha de Nacimiento"], datos["Usuario"], datos["Contraseña"], datos["Especialidad (opcional)"]))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Usuario registrado exitosamente")
                self.reg_window.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El usuario ya existe")
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios")

    def menu(self, user):
        self.user = user
        self.frame = tk.Frame(self.window, bg="light blue")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Nombre", "Apellidos", "Edad", "Teléfono", "Dirección", "Fecha", "Hora", "Médico", "Especialidad", "Estado"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Apellidos", text="Apellidos")
        self.tree.heading("Edad", text="Edad")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Dirección", text="Dirección")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Médico", text="Médico")
        self.tree.heading("Especialidad", text="Especialidad")
        self.tree.heading("Estado", text="Estado")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_frame = tk.Frame(self.frame, bg="light blue")
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.button_agendar = tk.Button(button_frame, text="Agendar Cita", command=self.agendar_cita, bg="light green")
        self.button_agendar.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.button_cancelar = tk.Button(button_frame, text="Cancelar Cita", command=self.cancelar_cita, bg="light green")
        self.button_cancelar.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.button_modificar = tk.Button(button_frame, text="Modificar Cita", command=self.modificar_cita, bg="light green")
        self.button_modificar.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.button_logout = tk.Button(button_frame, text="Cerrar Sesión", command=self.logout, bg="light green")
        self.button_logout.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.actualizar_tabla_citas()

    def actualizar_tabla_citas(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cursor.execute("SELECT * FROM citas")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    def agendar_cita(self):
        if self.user[6] != "Administrador" and self.user[6] is None:
            messagebox.showerror("Error", "Solo el administrador o los médicos pueden agendar citas")
            return

        self.agendar_window = tk.Toplevel(self.window)
        self.agendar_window.title("Agendar Cita")
        self.agendar_window.geometry("400x400")
        self.agendar_window.config(bg="light blue")

        self.agendar_frame = tk.LabelFrame(self.agendar_window, text="Agendar Cita", bg="light blue")
        self.agendar_frame.pack(pady=20)

        labels = ["Nombre", "Apellidos", "Edad", "Teléfono", "Dirección", "Fecha", "Hora", "Especialidad"]
        self.cita_entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.agendar_frame, text=label + ":", bg="light blue").grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(self.agendar_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.cita_entries[label] = entry

        self.label_medico = tk.Label(self.agendar_frame, text="Médico:", bg="light blue")
        self.label_medico.grid(row=len(labels), column=0, padx=5, pady=5)

        self.medico_var = tk.StringVar(self.agendar_frame)
        self.cursor.execute("SELECT nombres, apellidos FROM usuarios WHERE especialidad IS NOT NULL")
        medicos = [f"{row[0]} {row[1]}" for row in self.cursor.fetchall()]
        self.medico_menu = ttk.Combobox(self.agendar_frame, textvariable=self.medico_var, values=medicos)
        self.medico_menu.grid(row=len(labels), column=1, padx=5, pady=5)

        self.button_save_cita = tk.Button(self.agendar_frame, text="Guardar", command=self.guardar_cita, bg="light green")
        self.button_save_cita.grid(row=len(labels) + 1, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

        self.button_back = tk.Button(self.agendar_frame, text="Atrás", command=self.agendar_window.destroy, bg="light green")
        self.button_back.grid(row=len(labels) + 2, column=0, padx=5, pady=5, sticky="WE")

    def guardar_cita(self):
        datos_cita = {label: entry.get() for label, entry in self.cita_entries.items()}
        medico = self.medico_var.get()
        if all(datos_cita.values()) and medico:
            try:
                self.cursor.execute("INSERT INTO citas (nombre, apellidos, edad, telefono, direccion, fecha, hora, medico, especialidad, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (datos_cita["Nombre"], datos_cita["Apellidos"], datos_cita["Edad"], datos_cita["Teléfono"], datos_cita["Dirección"], datos_cita["Fecha"], datos_cita["Hora"], medico, datos_cita["Especialidad"], "Pendiente"))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Cita agendada exitosamente")
                self.agendar_window.destroy()
                self.actualizar_tabla_citas()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al agendar la cita: {e}")
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios")

    def cancelar_cita(self):
        selected_item = self.tree.selection()
        if selected_item:
            cita_id = self.tree.item(selected_item)['values'][0]
            try:
                self.cursor.execute("UPDATE citas SET estado='Cancelada' WHERE id=?", (cita_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Cita cancelada exitosamente")
                self.actualizar_tabla_citas()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al cancelar la cita: {e}")
        else:
            messagebox.showerror("Error", "Por favor, seleccione una cita")

    def modificar_cita(self):
        selected_item = self.tree.selection()
        if selected_item:
            cita_id = self.tree.item(selected_item)['values'][0]
            self.modificar_window = tk.Toplevel(self.window)
            self.modificar_window.title("Modificar Cita")
            self.modificar_window.geometry("400x400")
            self.modificar_window.config(bg="light blue")

            self.modificar_frame = tk.LabelFrame(self.modificar_window, text="Modificar Cita", bg="light blue")
            self.modificar_frame.pack(pady=20)

            labels = ["Nombre", "Apellidos", "Edad", "Teléfono", "Dirección", "Fecha", "Hora", "Especialidad"]
            self.modificar_entries = {}

            for i, label in enumerate(labels):
                tk.Label(self.modificar_frame, text=label + ":", bg="light blue").grid(row=i, column=0, padx=5, pady=5)
                entry = tk.Entry(self.modificar_frame)
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.modificar_entries[label] = entry

            self.label_medico = tk.Label(self.modificar_frame, text="Médico:", bg="light blue")
            self.label_medico.grid(row=len(labels), column=0, padx=5, pady=5)

            self.medico_var = tk.StringVar(self.modificar_frame)
            self.cursor.execute("SELECT nombres, apellidos FROM usuarios WHERE especialidad IS NOT NULL")
            medicos = [f"{row[0]} {row[1]}" for row in self.cursor.fetchall()]
            self.medico_menu = ttk.Combobox(self.modificar_frame, textvariable=self.medico_var, values=medicos)
            self.medico_menu.grid(row=len(labels), column=1, padx=5, pady=5)

            self.button_save_modificar = tk.Button(self.modificar_frame, text="Guardar", command=lambda: self.guardar_modificacion(cita_id), bg="light green")
            self.button_save_modificar.grid(row=len(labels) + 1, column=0, columnspan=2, padx=5, pady=5, sticky="WE")

            self.button_back = tk.Button(self.modificar_frame, text="Atrás", command=self.modificar_window.destroy, bg="light green")
            self.button_back.grid(row=len(labels) + 2, column=0, padx=5, pady=5, sticky="WE")

            self.cursor.execute("SELECT * FROM citas WHERE id=?", (cita_id,))
            cita = self.cursor.fetchone()
            if cita:
                for i, label in enumerate(labels):
                    self.modificar_entries[label].insert(0, cita[i + 1])
                self.medico_var.set(cita[8])
        else:
            messagebox.showerror("Error", "Por favor, seleccione una cita")

    def guardar_modificacion(self, cita_id):
        datos_cita = {label: entry.get() for label, entry in self.modificar_entries.items()}
        medico = self.medico_var.get()
        if all(datos_cita.values()) and medico:
            try:
                self.cursor.execute("UPDATE citas SET nombre=?, apellidos=?, edad=?, telefono=?, direccion=?, fecha=?, hora=?, medico=?, especialidad=? WHERE id=?",
                                    (datos_cita["Nombre"], datos_cita["Apellidos"], datos_cita["Edad"], datos_cita["Teléfono"], datos_cita["Dirección"], datos_cita["Fecha"], datos_cita["Hora"], medico, datos_cita["Especialidad"], cita_id))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Cita modificada exitosamente")
                self.modificar_window.destroy()
                self.actualizar_tabla_citas()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al modificar la cita: {e}")
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios")

    def logout(self):
        self.frame.destroy()
        self.__init__(self.window)

    def close_db(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = CitasMedicas(root)
    root.mainloop()