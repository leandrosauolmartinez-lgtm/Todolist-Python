#!/usr/bin/env python3
"""Lista de tareas con interfaz gráfica (Tkinter). Guarda en tareas.json."""
import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

ARCHIVO = Path(__file__).with_name("tareas.json")


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mi lista de tareas")
        self.geometry("520x560")
        self.minsize(420, 420)
        self.tareas = self.cargar()
        self.filtro = tk.StringVar(value="todas")
        self.crear_widgets()
        self.refrescar()
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    # ---------- datos ----------
    def cargar(self):
        try:
            return json.loads(ARCHIVO.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def guardar(self):
        ARCHIVO.write_text(json.dumps(self.tareas, ensure_ascii=False, indent=2),
                           encoding="utf-8")

    # ---------- interfaz ----------
    def crear_widgets(self):
        ttk.Style(self).theme_use("clam")
        marco = ttk.Frame(self, padding=12)
        marco.pack(fill="both", expand=True)

        ttk.Label(marco, text="📝 Mis tareas", font=("Segoe UI", 16, "bold")).pack(anchor="w")

        fila = ttk.Frame(marco)
        fila.pack(fill="x", pady=(10, 6))
        self.entrada = ttk.Entry(fila, font=("Segoe UI", 11))
        self.entrada.pack(side="left", fill="x", expand=True, ipady=4)
        self.entrada.bind("<Return>", lambda e: self.agregar())
        self.entrada.focus()
        ttk.Button(fila, text="Agregar", command=self.agregar).pack(side="left", padx=(6, 0))

        filtros = ttk.Frame(marco)
        filtros.pack(fill="x", pady=4)
        for texto, valor in (("Todas", "todas"), ("Pendientes", "pendientes"),
                             ("Hechas", "hechas")):
            ttk.Radiobutton(filtros, text=texto, value=valor, variable=self.filtro,
                            command=self.refrescar).pack(side="left", padx=(0, 10))

        cont = ttk.Frame(marco)
        cont.pack(fill="both", expand=True)
        self.lista = tk.Listbox(cont, font=("Segoe UI", 12), activestyle="none",
                                selectmode="single", relief="flat", highlightthickness=1)
        barra = ttk.Scrollbar(cont, command=self.lista.yview)
        self.lista.config(yscrollcommand=barra.set)
        self.lista.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.lista.bind("<Double-Button-1>", lambda e: self.alternar())

        botones = ttk.Frame(marco)
        botones.pack(fill="x", pady=8)
        for texto, cmd in (("✔ Completar", self.alternar), ("✏ Editar", self.editar),
                           ("🗑 Eliminar", self.eliminar),
                           ("Limpiar hechas", self.limpiar)):
            ttk.Button(botones, text=texto, command=cmd).pack(side="left", padx=(0, 6))

        self.progreso = ttk.Progressbar(marco, maximum=100)
        self.progreso.pack(fill="x")
        self.estado = ttk.Label(marco, text="")
        self.estado.pack(anchor="w", pady=(4, 0))

    # ---------- lógica ----------
    def visibles(self):
        f = self.filtro.get()
        return [(i, t) for i, t in enumerate(self.tareas)
                if f == "todas" or (f == "hechas") == t["hecha"]]

    def refrescar(self):
        self.indices = []
        self.lista.delete(0, "end")
        for i, t in self.visibles():
            marca = "☑" if t["hecha"] else "☐"
            self.lista.insert("end", f" {marca}  {t['texto']}   · {t['fecha']}")
            if t["hecha"]:
                self.lista.itemconfig("end", fg="#888888")
            self.indices.append(i)
        hechas = sum(t["hecha"] for t in self.tareas)
        total = len(self.tareas)
        self.progreso["value"] = (hechas / total * 100) if total else 0
        self.estado.config(text=f"{hechas} de {total} completadas")

    def seleccionada(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showinfo("Selecciona una tarea", "Primero elige una tarea de la lista.")
            return None
        return self.indices[sel[0]]

    def agregar(self):
        texto = self.entrada.get().strip()
        if not texto:
            return
        self.tareas.append({"texto": texto, "hecha": False,
                            "fecha": datetime.now().strftime("%d/%m/%Y")})
        self.entrada.delete(0, "end")
        self.guardar()
        self.refrescar()

    def alternar(self):
        i = self.seleccionada()
        if i is not None:
            self.tareas[i]["hecha"] = not self.tareas[i]["hecha"]
            self.guardar()
            self.refrescar()

    def editar(self):
        i = self.seleccionada()
        if i is None:
            return
        nuevo = simpledialog.askstring("Editar tarea", "Nuevo texto:",
                                       initialvalue=self.tareas[i]["texto"], parent=self)
        if nuevo and nuevo.strip():
            self.tareas[i]["texto"] = nuevo.strip()
            self.guardar()
            self.refrescar()

    def eliminar(self):
        i = self.seleccionada()
        if i is not None and messagebox.askyesno("Eliminar", f"¿Eliminar «{self.tareas[i]['texto']}»?"):
            self.tareas.pop(i)
            self.guardar()
            self.refrescar()

    def limpiar(self):
        if any(t["hecha"] for t in self.tareas) and messagebox.askyesno(
                "Limpiar", "¿Borrar todas las tareas completadas?"):
            self.tareas = [t for t in self.tareas if not t["hecha"]]
            self.guardar()
            self.refrescar()

    def cerrar(self):
        self.guardar()
        self.destroy()


if __name__ == "__main__":
    TodoApp().mainloop()