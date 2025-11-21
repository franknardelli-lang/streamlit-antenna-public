"""
Antenna Radiation Pattern Visualization Tool

This script provides a graphical user interface (GUI) application for loading,
analyzing, and visualizing antenna radiation pattern data from processed CSV files.

Key Features:
- Loads multiple CSV files from a user-selected folder where filenames end with '_processed.csv'.
- Parses each CSV into a pandas DataFrame if it contains at least 4 columns.
- Allows the user to select one or more variables (datasets) to plot via a multi-select listbox.
- Accepts user input for isotropic power (in dBm) and a custom plot title.
- Computes and plots polar radiation patterns using matplotlib with:
    * Conversion from field strength (dBuV/m) to power (dBm).
    * Polar plots with theta=0 at North and clockwise direction.
    * Multiple datasets plotted with distinct colors.
    * Dynamic plot limits and a detailed legend showing max, min, average power, and efficiency.
- Enables saving the generated plot as a high-resolution JPEG file.
- Responsive GUI built with Tkinter:
    * Modal dialogs for variable selection.
    * Embedded matplotlib plots within the main window.
    * Buttons for re-running variable selection, saving plots, and exiting.

Dependencies:
- Python standard libraries: os, tkinter
- Third-party libraries: numpy, pandas, matplotlib

Usage:
- Run the script.
- Select the folder containing your processed CSV files.
- Choose variables to plot, enter isotropic power and plot title.
- View the polar plot, re-run selection if needed, and save the plot as JPEG.

This tool is useful for antenna engineers and researchers analyzing radiation patterns
and comparing multiple datasets visually and quantitatively.

Author: [Your Name]
Date: [Date]
"""
"""
CSV File Format Requirement:
- The script expects each processed CSV file to have at least 4 columns.
- Column 0: Angle values in degrees (used as the angular coordinate for plotting).
- Column 3: Total field strength values in dBµV/m (used for power calculation and plotting).
- Other columns are ignored by the plotting function but must be present to meet the minimum column count.
"""
"""
File Naming Convention:
- The script processes only CSV files with filenames ending in '_processed.csv'.
- Ensure your processed data files follow this naming pattern for the script to recognize and process them.
"""


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def load_data():
    folder_path = filedialog.askdirectory(title='Select folder containing processed CSV files')
    if not folder_path:
        print('No folder selected.')
        return {}

    data_dict = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('_processed.csv'):
            filepath = os.path.join(folder_path, filename)
            try:
                df = pd.read_csv(filepath)
                if df.shape[1] >= 4:
                    base_name = filename.replace('_processed.csv', '')
                    var_name = base_name + '_totalField'
                    data_dict[var_name] = df
                    print(f'Loaded {filename} as {var_name}')
                else:
                    print(f'Skipping {filename}: fewer than 4 columns.')
            except Exception as e:
                print(f'Error loading {filename}: {e}')
    return data_dict

def select_variables(data_dict, root):
    # Custom dialog for variable selection, iso power, plot title
    dialog = tk.Toplevel(root)
    dialog.title("Select Variables")
    dialog.grab_set()  # Modal

    selected_vars = []
    iso_power = 0.0
    plot_title = ''

    # Listbox for variables
    tk.Label(dialog, text='Select variables to plot:').grid(row=0, column=0, sticky='w')
    listbox = tk.Listbox(dialog, selectmode=tk.MULTIPLE, height=10, width=40, exportselection=False)
    for var in data_dict.keys():
        listbox.insert(tk.END, var)
    listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Entry for iso power
    tk.Label(dialog, text='Isotropic Power (dBm):').grid(row=2, column=0, sticky='w')
    iso_entry = tk.Entry(dialog)
    iso_entry.insert(0, '0')
    iso_entry.grid(row=2, column=1, padx=5, pady=5)

    # Entry for plot title
    tk.Label(dialog, text='Plot Title:').grid(row=3, column=0, sticky='w')
    title_entry = tk.Entry(dialog)
    title_entry.grid(row=3, column=1, padx=5, pady=5)

    # Buttons
    def on_ok():
        selected_indices = listbox.curselection()
        nonlocal selected_vars, iso_power, plot_title
        selected_vars = [listbox.get(i) for i in selected_indices]
        try:
            iso_power = float(iso_entry.get())
        except:
            messagebox.showwarning("Invalid Input", "Invalid isotropic power. Using 0 dBm.")
            iso_power = 0
        plot_title = title_entry.get()
        dialog.destroy()

    def on_cancel():
        nonlocal selected_vars, iso_power, plot_title
        selected_vars = []
        iso_power = 0
        plot_title = ''
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
    tk.Button(btn_frame, text='Plot', command=on_ok).pack(side='left', padx=5)
    tk.Button(btn_frame, text='Cancel', command=on_cancel).pack(side='left', padx=5)

    dialog.wait_window()
    return selected_vars, iso_power, plot_title

def create_polar_plot(data_dict, selected_vars, iso_power_dBm, plot_title, figsize=(12,8)):
    fig, ax = plt.subplots(subplot_kw={'projection':'polar'}, figsize=figsize)
    plt.subplots_adjust(bottom=0.15)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    colors = plt.cm.jet(np.linspace(0, 1, len(selected_vars)))
    legend_entries = []

    P_iso_linear = 10**(iso_power_dBm/10) / 1000  # Watts
    all_P_dBm = []

    for i, var_name in enumerate(selected_vars):
        df = data_dict[var_name]
        angles_deg = df.iloc[:, 0].values
        field_dBuV_m = df.iloc[:, 3].values

        E_V_per_m = 10**((field_dBuV_m - 120)/20)
        P_watts = (E_V_per_m**2 * 3**2) / 30
        P_watts[P_watts < 1e-15] = 1e-15
        P_dBm = 10 * np.log10(P_watts * 1000)

        theta = np.deg2rad(angles_deg)
        theta = np.append(theta, theta[0])
        P_dBm = np.append(P_dBm, P_dBm[0])
        ax.plot(theta, P_dBm, label=var_name, linewidth=1.5, color=colors[i])

        P_linear = 10**(P_dBm/10) / 1000
        avg_power = np.mean(P_linear)
        efficiency = (avg_power / P_iso_linear) * 100
        max_dBm = np.max(P_dBm)
        min_dBm = np.min(P_dBm)
        avg_dBm = 10 * np.log10(avg_power * 1000)
        eff_dB = 10 * np.log10(efficiency / 100)

        legend_entries.append(
            f"{var_name}\nmax->{max_dBm:.1f} dBm, min->{min_dBm:.1f} dBm"
            f"\navg->{avg_dBm:.1f} dBm\neff->{efficiency:.1f}% ({eff_dB:.1f} dB)"
        )

        all_P_dBm.extend(P_dBm[:-1])

    if all_P_dBm:
        ax.set_rlim([np.floor(np.min(all_P_dBm))-5, np.ceil(np.max(all_P_dBm))+5])
    else:
        ax.set_rlim([-10, 10])

    ax.set_title(plot_title)

    if legend_entries:
        lgd = ax.legend(legend_entries, loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=8)
        plt.setp(lgd.get_texts(), linespacing=1.2)

    return fig

def save_plot(figure, plot_title, root):
    default_name = plot_title if plot_title else 'plot'
    default_path = default_name + '.jpg'
    filename = filedialog.asksaveasfilename(
        defaultextension='.jpg',
        filetypes=[("JPEG files", "*.jpg")],
        initialfile=default_name + ".jpg",
        parent=root
    )
    if filename:
        try:
            figure.savefig(filename, dpi=300)
            messagebox.showinfo('Success', f'Plot saved as {filename}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save: {e}')

def main():
    root = tk.Tk()
    root.title("Antenna Radiation Pattern")
    root.geometry("1400x900")
    root.minsize(1400, 850)

    # Load data
    data = load_data()
    if not data:
        messagebox.showinfo('Info', 'No data loaded. Exiting.')
        root.destroy()
        return

    # Variable selection
    selected_vars, iso_power_dBm, plot_title = select_variables(data, root)
    if not selected_vars:
        messagebox.showinfo('Info', 'No variables selected. Exiting.')
        root.destroy()
        return

    # Create main canvas for plot
    canvas_frame = tk.Frame(root)
    canvas_frame.pack(fill='both', expand=True)
    canvas = tk.Canvas(canvas_frame)
    canvas.pack(fill='both', expand=True)

    # Buttons frame
    btn_frame = tk.Frame(root)
    btn_frame.pack(fill='x', pady=5)

    def draw_plot():
        # Clear previous plot
        for widget in canvas_frame.winfo_children():
            widget.destroy()

        # Create figure
        width, height = 800, 600
        figsize = (width/100, height/100)
        fig = create_polar_plot(data, selected_vars, iso_power_dBm, plot_title, figsize=figsize)

        # Embed in Tkinter
        figure_canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        figure_canvas.draw()
        figure_widget = figure_canvas.get_tk_widget()
        figure_widget.pack(fill='both', expand=True)
        return figure_canvas

    # Initial plot
    fig_canvas = draw_plot()

    def rerun():
        nonlocal selected_vars, iso_power_dBm, plot_title, fig_canvas
        new_vars, new_iso_power, new_plot_title = select_variables(data, root)
        if new_vars:
            selected_vars = new_vars
            iso_power_dBm = new_iso_power
            plot_title = new_plot_title
            # Redraw plot
            fig_canvas.get_tk_widget().destroy()
            fig_canvas = draw_plot()

    def on_save_plot():
        if fig_canvas:
            save_plot(fig_canvas.figure, plot_title, root)

    def on_exit():
        root.destroy()

    # Buttons
    tk.Button(btn_frame, text='Rerun', command=rerun).pack(side='left', padx=5)
    tk.Button(btn_frame, text='Save Plot', command=on_save_plot).pack(side='left', padx=5)
    tk.Button(btn_frame, text='Exit', command=on_exit).pack(side='left', padx=5)

    root.mainloop()

if __name__ == '__main__':
    main()