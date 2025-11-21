import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
import math

def compute_distance(f_mhz, n, pt, gt, gr, ltx, lrx, loth, fm, sens):
    """Return distance in km and path loss."""
    k = 32.44
    numerator = pt + gt + gr - (ltx + lrx + loth) - fm - sens - k - 20 * math.log10(f_mhz)
    d_km = 10 ** (numerator / (10 * n))
    lp = k + 20 * math.log10(f_mhz) + 10 * n * math.log10(d_km)
    return d_km, lp

# --- Setup figure ---
fig, ax = plt.subplots(figsize=(9, 7))
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
ax.axis("off")

# --- Parameter defaults ---
params = {
    "Frequency (MHz)": 2400.0,
    "Path Loss Exponent (n)": 2.0,
    "Tx Power (dBm)": 20.0,
    "Tx Antenna Gain (dBi)": 2.0,
    "Rx Antenna Gain (dBi)": 2.0,
    "Tx Losses (dB)": 1.0,
    "Rx Losses (dB)": 1.0,
    "Other Losses (dB)": 0.0,
    "Fade Margin (dB)": 10.0,
    "Rx Sensitivity (dBm)": -90.0
}

# --- Create textboxes dynamically ---
boxes = {}
start_y = 0.9
dy = 0.075  # spacing between rows

for i, (label, default) in enumerate(params.items()):
    y = start_y - i * dy
    # label column
    ax.text(0.05, y, label, va="center", ha="left", fontsize=10)
    # textbox column (further left to prevent overlap)
    axbox = plt.axes([0.25, y - 0.025, 0.15, 0.045])
    box = TextBox(axbox, "", initial=str(default))
    boxes[label] = box

# --- Output text area on the right ---
output_ax = plt.axes([0.45, 0.15, 0.5, 0.75])
output_ax.axis("off")
output_text = output_ax.text(0, 1, "", va="top", ha="left", fontsize=11, family="monospace")

# --- Calculate button ---
button_ax = plt.axes([0.25, 0.05, 0.15, 0.06])
calc_button = Button(button_ax, "Calculate", color="lightblue", hovercolor="skyblue")

def on_calculate(event):
    try:
        vals = {k: float(box.text) for k, box in boxes.items()}
        d_km, lp = compute_distance(
            vals["Frequency (MHz)"],
            vals["Path Loss Exponent (n)"],
            vals["Tx Power (dBm)"],
            vals["Tx Antenna Gain (dBi)"],
            vals["Rx Antenna Gain (dBi)"],
            vals["Tx Losses (dB)"],
            vals["Rx Losses (dB)"],
            vals["Other Losses (dB)"],
            vals["Fade Margin (dB)"],
            vals["Rx Sensitivity (dBm)"],
        )

        d_m = d_km * 1000
        d_mi = d_km * 0.621371
        d_ft = d_m * 3.28084

        text = (
            f"=== Results ===\n"
            f"Distance: {d_km:.3f} km\n"
            f"          {d_m:.1f} m\n"
            f"          {d_mi:.3f} miles\n"
            f"          {d_ft:.0f} ft\n\n"
            f"Path Loss: {lp:.2f} dB\n"
        )
        output_text.set_text(text)
        fig.canvas.draw_idle()
    except Exception as e:
        output_text.set_text(f"Error: {e}")
        fig.canvas.draw_idle()

calc_button.on_clicked(on_calculate)

plt.show()
