"""
This script models and visualizes the impact of parasitic load matching on the power delivered to an antenna in a RF system.

Key features:
- The transmitter power (in dBm) and the antenna return loss (RL) are configurable parameters.
- The script calculates the parasitic load impedance based on its return loss, assuming a range from 0 dB (poor match) to 20 dB (good match).
- It computes the combined load impedance formed by the antenna and the parasitic load in parallel.
- From the combined impedance, it derives the reflection coefficient and the total power delivered to the load.
- The power delivered specifically to the antenna is proportional to its conductance relative to the total conductance of both loads.
- Finally, it plots the power delivered to the antenna (in dBm) as a function of the parasitic load's return loss.

Usage:
- Adjust the 'RL_antenna_dB' variable to set the antenna's return loss.
- Adjust the 'P_tx_dBm' variable to set the transmitter power.
- Run the script to generate a plot showing how the antenna power varies with parasitic load matching.

This model helps in understanding how parasitic load matching affects antenna efficiency and system performance in RF design.
"""


import numpy as np
import matplotlib.pyplot as plt

# Constants
Z0 = 50  # system impedance (ohms)
P_tx_dBm = 20  # transmitter power in dBm
P_tx_mW = 10**(P_tx_dBm / 10)

# Antenna return loss fixed at 10 dB
RL_antenna_dB = 10
Gamma_A = 10 ** (-RL_antenna_dB / 20)
Z_A = Z0 * (1 + Gamma_A) / (1 - Gamma_A)
G_A = 1 / Z_A

# Parasitic return loss range from 0 to 20 dB
RL_parasitic_dB = np.linspace(0, 20, 100)
Gamma_p = 10 ** (-RL_parasitic_dB / 20)
Z_p = Z0 * (1 + Gamma_p) / (1 - Gamma_p)
G_p = 1 / Z_p

# Combined admittance and impedance
G_total = G_A + G_p
Z_total = 1 / G_total

# Reflection coefficient of combined load
Gamma_total = (Z_total - Z0) / (Z_total + Z0)
Gamma_total_mag = np.abs(Gamma_total)

# Power delivered to combined load
P_delivered_mW = P_tx_mW * (1 - Gamma_total_mag**2)

# Power split between antenna and parasitic load (proportional to conductance)
P_antenna_mW = P_delivered_mW * (G_A / G_total)

# Convert power to dBm
P_antenna_dBm = 10 * np.log10(P_antenna_mW)

# Plot
plt.figure(figsize=(8,6))
plt.plot(RL_parasitic_dB, P_antenna_dBm, label='Power to Antenna')
plt.xlabel('Parasitic Return Loss (dB)')
plt.ylabel('Power Delivered to Antenna (dBm)')
plt.title('Power to Antenna vs Parasitic Return Loss (Tx Power 20 dBm Antenna RL = 10 dB)')
plt.grid(True)
plt.legend()
plt.gca().invert_xaxis()  # Invert x-axis: 0 dB (bad match) on right, 20 dB (good match) on left
plt.show()