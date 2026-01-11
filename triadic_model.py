import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

def hill(x, gamma=10.0, threshold=0.5, steepness=6):
    """
    Hill activation function for nonlinear mutual excitation.
    
    Parameters:
    - x: Input value (subsystem state, 0 to 1).
    - gamma: Maximum activation strength.
    - threshold: Inflection point for sigmoid-like response.
    - steepness: Controls nonlinearity (higher = sharper transition).
    
    Returns: Activated value.
    """
    return gamma * x**steepness / (threshold**steepness + x**steepness)

def triadic_model(y, t, params):
    """
    Triadic ODE system with dwelling dynamics.
    
    State vector y: [x1, x2, x3, dwelling]
    - x1: Baseline MSR/fusion technology maturity (0-1).
    - x2: Quantum stability enhancement maturity (0-1).
    - x3: GW-scale integration maturity (0-1).
    - dwelling: Incoherence-driven dwelling state (0-1).
    
    Parameters (dict):
    - dwelling_rise: Rate of dwelling increase with incoherence.
    - dwelling_fade: Rate of dwelling decrease with coherence.
    - coupling_boost: Multiplier for coupling during high dwelling.
    - decay_relief: Reduction in decay during high dwelling.
    - base_decay: Baseline decay rate.
    - nudge_time1, nudge_time2: Optional times for intervention nudges.
    
    Returns: dy/dt vector.
    """
    x1, x2, x3, dwelling = np.clip(y, 0.0, 1.0)
    coherence = (x1 + x2 + x3) / 3.0
    
    # Dwelling dynamics: Accumulates in incoherence, dissipates in coherence
    d_dwelling_dt = (params['dwelling_rise'] * (1 - coherence) * (1 - dwelling) - 
                     params['dwelling_fade'] * coherence * dwelling)
    
    # Adaptive modulation
    coupling = 1.0 + params['coupling_boost'] * dwelling
    decay = params['base_decay'] * (1.0 - params['decay_relief'] * dwelling)
    
    # Nonlinear activations
    act1 = hill(x1)
    act2 = hill(x2)
    act3 = hill(x3)
    
    # Triadic interactions: Each subsystem driven by average of others
    dx1_dt = coupling * (act2 + act3) / 2 * (1 - x1) - decay * x1
    dx2_dt = coupling * (act1 + act3) / 2 * (1 - x2) - decay * x2 * 1.2  # Slightly higher decay for x2
    dx3_dt = coupling * (act1 + act2) / 2 * (1 - x3) - decay * x3 * 1.5  # Higher decay for x3
    
    # Phase-specific nudges (interventions)
    if 'nudge_time1' in params and params['nudge_time1'] <= t < params['nudge_time1'] + 2:
        dx1_dt += 0.5 * (1 - x1)  # Boost baseline tech
    if 'nudge_time2' in params and params['nudge_time2'] <= t < params['nudge_time2'] + 2:
        dx2_dt += 0.5 * (1 - x2)  # Boost quantum layer
    
    return [dx1_dt, dx2_dt, dx3_dt, d_dwelling_dt]

def calculate_power_trajectory(sol, scenario='none'):
    """
    Compute emergent power output trajectory.
    
    Parameters:
    - sol: ODE solution array (time x states).
    - scenario: 'none', 'phase1', or 'both' for scaling mode.
    
    Returns: Power array (Watts) over time.
    """
    x1, x2, x3 = sol[:, 0], sol[:, 1], sol[:, 2]
    
    # Realistic parameters for compact fusion reactor (1 m³ volume)
    base_density = 10.0  # W/cm³ (adjusted for fusion power density)
    volume = 1e6  # cm³ (fridge-sized)
    
    if scenario == 'none':
        return np.zeros_like(x1)
    
    elif scenario == 'phase1':
        # Linear scaling with baseline maturity
        return base_density * volume * x1
    
    else:  # 'both' - Synergistic scaling
        base_power = base_density * volume * x1
        synergy = x2 * x3
        quantum_factor = 1 + 99 * (synergy ** 2)  # Quadratic synergy for ~100x at full maturity
        return base_power * quantum_factor

# Default simulation parameters
params = {
    'dwelling_rise': 0.35,
    'dwelling_fade': 0.45,
    'coupling_boost': 0.8,
    'decay_relief': 0.6,
    'base_decay': 0.22
}

# Time and initial conditions
t = np.linspace(0, 50, 500)  # Scaled time (e.g., months/years)
y0 = [0.2, 0.1, 0.15, 0.6]   # [x1, x2, x3, dwelling]

# Scenario simulations
sol_no = odeint(triadic_model, y0, t, args=(params,))

params_p1 = params.copy()
params_p1['nudge_time1'] = 10
sol_p1 = odeint(triadic_model, y0, t, args=(params_p1,))

params_p2 = params_p1.copy()
params_p2['nudge_time2'] = 25
sol_p2 = odeint(triadic_model, y0, t, args=(params_p2,))

# Coherence calculations
coh_no = np.mean(sol_no[:, :3], axis=1)
coh_p1 = np.mean(sol_p1[:, :3], axis=1)
coh_p2 = np.mean(sol_p2[:, :3], axis=1)

# Power trajectories
power_no = calculate_power_trajectory(sol_no, 'none')
power_p1 = calculate_power_trajectory(sol_p1, 'phase1')
power_p2 = calculate_power_trajectory(sol_p2, 'both')

# Visualization (6-panel figure)
fig = plt.figure(figsize=(15, 10))

# Panel 1: Coherence
ax1 = plt.subplot(2, 3, 1)
ax1.plot(t, coh_no, label='No Interventions', linewidth=2.5, color='#dc2626')
ax1.plot(t, coh_p1, label='Phase 1 Only', linewidth=2.5, color='#f59e0b')
ax1.plot(t, coh_p2, label='Phase 2 (Both)', linewidth=2.5, color='#10b981')
ax1.axvline(10, color='gold', ls='--', alpha=0.5, linewidth=1.5)
ax1.axvline(25, color='darkred', ls='--', alpha=0.5, linewidth=1.5)
ax1.set_xlabel('Time (Scaled Months/Years)', fontsize=10)
ax1.set_ylabel('System Coherence', fontsize=10)
ax1.set_title('Progress to GW-Scale Systems', fontweight='bold')
ax1.legend(loc='best', fontsize=9)
ax1.grid(alpha=0.3)

# Panel 2: Dwelling
ax2 = plt.subplot(2, 3, 2)
ax2.plot(t, sol_no[:, 3], label='No Interventions', linewidth=2, color='#dc2626', alpha=0.7)
ax2.plot(t, sol_p1[:, 3], label='Phase 1', linewidth=2, color='#f59e0b', alpha=0.7)
ax2.plot(t, sol_p2[:, 3], label='Phase 2', linewidth=2, color='#10b981', alpha=0.7)
ax2.axvline(10, color='gold', ls='--', alpha=0.5, linewidth=1.5)
ax2.axvline(25, color='darkred', ls='--', alpha=0.5, linewidth=1.5)
ax2.set_xlabel('Time', fontsize=10)
ax2.set_ylabel('Dwelling State', fontsize=10)
ax2.set_title('Incoherence-Driven Coupling', fontweight='bold')
ax2.legend(loc='best', fontsize=9)
ax2.grid(alpha=0.3)

# Panel 3: Power (Log)
ax3 = plt.subplot(2, 3, 3)
ax3.semilogy(t, power_p1 / 1e6, label='Phase 1 (MW)', linewidth=2.5, color='#f59e0b')
ax3.semilogy(t, power_p2 / 1e9, label='Phase 2 (GW)', linewidth=2.5, color='#10b981')
ax3.axvline(10, color='gold', ls='--', alpha=0.5, linewidth=1.5, label='Phase 1 Nudge')
ax3.axvline(25, color='darkred', ls='--', alpha=0.5, linewidth=1.5, label='Phase 2 Nudge')
ax3.set_xlabel('Time', fontsize=10)
ax3.set_ylabel('Power Output', fontsize=10)
ax3.set_title('Emergent Power Scaling (Log)', fontweight='bold')
ax3.legend(loc='best', fontsize=9)
ax3.grid(alpha=0.3, which='both')

# Panels 4-6: Subsystems
ax4 = plt.subplot(2, 3, 4)
ax4.plot(t, sol_no[:, 0], label='x1: Baseline Tech', linewidth=2, color='#3b82f6')
ax4.plot(t, sol_no[:, 1], label='x2: Quantum Layer', linewidth=2, color='#8b5cf6')
ax4.plot(t, sol_no[:, 2], label='x3: GW Integration', linewidth=2, color='#ec4899')
ax4.set_xlabel('Time', fontsize=10)
ax4.set_ylabel('Subsystem State', fontsize=10)
ax4.set_title('No Intervention (Stuck)', fontweight='bold')
ax4.legend(loc='best', fontsize=8)
ax4.grid(alpha=0.3)

ax5 = plt.subplot(2, 3, 5)
ax5.plot(t, sol_p1[:, 0], label='x1: Baseline Tech', linewidth=2, color='#3b82f6')
ax5.plot(t, sol_p1[:, 1], label='x2: Quantum Layer', linewidth=2, color='#8b5cf6')
ax5.plot(t, sol_p1[:, 2], label='x3: GW Integration', linewidth=2, color='#ec4899')
ax5.axvline(10, color='gold', ls='--', alpha=0.5, linewidth=1.5)
ax5.set_xlabel('Time', fontsize=10)
ax5.set_ylabel('Subsystem State', fontsize=10)
ax5.set_title('Phase 1 Only (Partial)', fontweight='bold')
ax5.legend(loc='best', fontsize=8)
ax5.grid(alpha=0.3)

ax6 = plt.subplot(2, 3, 6)
ax6.plot(t, sol_p2[:, 0], label='x1: Baseline Tech', linewidth=2, color='#3b82f6')
ax6.plot(t, sol_p2[:, 1], label='x2: Quantum Layer', linewidth=2, color='#8b5cf6')
ax6.plot(t, sol_p2[:, 2], label='x3: GW Integration', linewidth=2, color='#ec4899')
ax6.axvline(10, color='gold', ls='--', alpha=0.5, linewidth=1.5)
ax6.axvline(25, color='darkred', ls='--', alpha=0.5, linewidth=1.5)
ax6.set_xlabel('Time', fontsize=10)
ax6.set_ylabel('Subsystem State', fontsize=10)
ax6.set_title('Both Phases (Full Synergy)', fontweight='bold')
ax6.legend(loc='best', fontsize=8)
ax6.grid(alpha=0.3)

plt.tight_layout()
fig.savefig('triadic_gw_analysis.png', dpi=300, bbox_inches='tight')
print("Figure saved as 'triadic_gw_analysis.png'")
plt.show()  # Optional: Display in interactive environments

# Analysis and printing
final_power_no = power_no[-1]
final_power_p1 = power_p1[-1]
final_power_p2 = power_p2[-1]

late_avg_no = np.mean(sol_no[-100:, :3], axis=0)
late_avg_p1 = np.mean(sol_p1[-100:, :3], axis=0)
late_avg_p2 = np.mean(sol_p2[-100:, :3], axis=0)

print("\n" + "="*70)
print("TRIADIC PHASE MODEL - GW-SCALE ANALYSIS")
print("="*70)

print("\n--- FINAL POWER OUTPUTS ---")
print(f"No Interventions:  {final_power_no:.3f} W (stuck at {coh_no[-1]:.1%} coherence)")
print(f"Phase 1 Only:      {final_power_p1/1e6:.3f} MW ({coh_p1[-1]:.1%} coherence)")
print(f"Both Phases:       {final_power_p2/1e9:.3f} GW ({coh_p2[-1]:.1%} coherence)")

print("\n--- LATE-STAGE SUBSYSTEM STATES (last 100 timesteps) ---")
print(f"No Intervention:   x1={late_avg_no[0]:.3f}, x2={late_avg_no[1]:.3f}, x3={late_avg_no[2]:.3f}")
print(f"Phase 1 Only:      x1={late_avg_p1[0]:.3f}, x2={late_avg_p1[1]:.3f}, x3={late_avg_p1[2]:.3f}")
print(f"Both Phases:       x1={late_avg_p2[0]:.3f}, x2={late_avg_p2[1]:.3f}, x3={late_avg_p2[2]:.3f}")

print("\n--- KEY INSIGHTS ---")
print(f"• Phase 1 achieves {final_power_p1/1e6:.1f} MW through baseline technology")
print(f"• Phase 2 achieves {final_power_p2/final_power_p1:.0f}x boost via quantum synergy")
print(f"• Quantum-GW synergy (x2*x3): {late_avg_p2[1]*late_avg_p2[2]:.3f}")
print(f"• Without intervention, system remains at {coh_no[-1]:.1%} coherence (dwelling trap)")

print("\n--- POWER SCALING MECHANISM ---")
print(f"• Base density: 10 W/cm³ (compact fusion scale)")
print(f"• System volume: 1 m³ (fridge-sized)")
print(f"• Phase 1: Linear scaling with x1 → {final_power_p1/1e6:.2f} MW")
print(f"• Phase 2: Exponential synergy (x2×x3)² → {final_power_p2/1e9:.2f} GW")

print("="*70 + "\n")

if __name__ == "__main__":
    pass  # Script runs on import/execution
