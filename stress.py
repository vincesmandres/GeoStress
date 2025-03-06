import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calcular_boussinesq(P, z_values, r):
    return (3 * P / (2 * np.pi * z_values**2)) * ((1 / (1 + (r / z_values)**2))**(5/2))

def calcular_westergaard(P, z_values, r, mu_s_values, z_estratos):
    sigma_westergaard = np.zeros_like(z_values)
    for i, z in enumerate(z_values):
        idx = np.searchsorted(z_estratos, z, side='right') - 1
        mu_s = mu_s_values[idx]
        eta = np.sqrt((1 - 2 * mu_s) / (2 - 2 * mu_s))
        I5 = (1 / (2 * np.pi * eta**2)) * (((r / (eta * z))**2 + 1)**(-3/2))
        sigma_westergaard[i] = (P / z**2) * I5
    return sigma_westergaard

def calcular_ponderada(sigma_boussinesq, sigma_westergaard, peso_boussinesq=0.5, peso_westergaard=0.5):
    return peso_boussinesq * sigma_boussinesq + peso_westergaard * sigma_westergaard

def graficar():
    try:
        P = float(entry_P.get())
        x = float(entry_x.get())
        y = float(entry_y.get())
        z_max = float(entry_z_max.get())
        capacidad_portante = float(entry_capacidad.get())
        profundidad_desplante = float(entry_desplante.get())
        activar_ponderada = ponderada_var.get()
        
        z_estratos = np.array([float(entry.get()) for entry in entries_z])
        mu_s = np.array([float(entry.get()) for entry in entries_mu])
        
        z_values = np.linspace(0.1, z_max, 100)
        r = np.sqrt(x**2 + y**2)
        
        sigma_boussinesq = calcular_boussinesq(P, z_values, r)
        sigma_westergaard = calcular_westergaard(P, z_values, r, mu_s, z_estratos)
        
        if activar_ponderada:
            sigma_ponderada = calcular_ponderada(sigma_boussinesq, sigma_westergaard)
        
        esfuerzo_desplante = np.interp(profundidad_desplante, z_values, sigma_ponderada if activar_ponderada else sigma_westergaard)
        
        if esfuerzo_desplante > capacidad_portante:
            mensaje = f"Profundidad insuficiente. Se recomienda aumentar la profundidad."
        else:
            mensaje = f"La profundidad de desplante es adecuada."
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot(sigma_boussinesq, z_values, label="Boussinesq", linestyle="solid", color="blue", marker='o', markevery=10)
        ax.plot(sigma_westergaard, z_values, label="Westergaard", linestyle="dashed", color="red", marker='s', markevery=10)
        
        if activar_ponderada:
            ax.plot(sigma_ponderada, z_values, label="Ponderada", linestyle="dashdot", color="green", marker='^', markevery=10)
        
        ax.axhline(y=profundidad_desplante, color='black', linestyle=':', label="Profundidad Desplante")
        ax.axvline(x=capacidad_portante, color='purple', linestyle='--', label="Capacidad Portante")
        
        ax.invert_yaxis()
        ax.set_xlabel(r'$\Delta \sigma_z$ [kN/m²]')
        ax.set_ylabel('Profundidad [m]')
        ax.set_title('Distribución de Esfuerzos Verticales')
        ax.legend()
        ax.grid()
        
        for widget in frame_right.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=frame_right)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        messagebox.showinfo("Verificación", mensaje)
    
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Interfaz gráfica
root = tk.Tk()
root.title("Cálculo de Esfuerzos Verticales y Verificación de Capacidad Portante")
root.geometry("1200x600")
root.resizable(True, True)

frame_left = ttk.Frame(root, padding=10)
frame_left.pack(side=tk.LEFT, fill=tk.Y)
frame_right = ttk.Frame(root, padding=10)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

ttk.Label(frame_left, text="Carga Puntual (P) [kN]:").pack()
entry_P = ttk.Entry(frame_left)
entry_P.pack(pady=5)

ttk.Label(frame_left, text="Posición X [m]:").pack()
entry_x = ttk.Entry(frame_left)
entry_x.pack(pady=5)

ttk.Label(frame_left, text="Posición Y [m]:").pack()
entry_y = ttk.Entry(frame_left)
entry_y.pack(pady=5)

ttk.Label(frame_left, text="Profundidad Máxima (z_max) [m]:").pack()
entry_z_max = ttk.Entry(frame_left)
entry_z_max.pack(pady=5)

ttk.Label(frame_left, text="Capacidad Portante [kN/m²]:").pack()
entry_capacidad = ttk.Entry(frame_left)
entry_capacidad.pack(pady=5)

ttk.Label(frame_left, text="Profundidad Desplante [m]:").pack()
entry_desplante = ttk.Entry(frame_left)
entry_desplante.pack(pady=5)

ponderada_var = tk.BooleanVar()
ttk.Checkbutton(frame_left, text="Activar Ponderada", variable=ponderada_var).pack()

ttk.Button(frame_left, text="Calcular", command=graficar).pack(pady=10)

root.mainloop()