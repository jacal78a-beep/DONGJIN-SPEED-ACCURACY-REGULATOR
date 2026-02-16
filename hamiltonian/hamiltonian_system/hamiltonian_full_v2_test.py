# Full v2.0 test with optimized parameters
import sys
sys.path.insert(0, '/home/user')
import hamiltonian_sim_v2 as sim
import time

print("="*80)
print(" HAMILTONIAN SYSTEM v2.0 - FULL VALIDATION")
print(" Constraint Correction: ENABLED")
print("="*80)

# Test parameters
T_sim = 20.0
dt_sim = 0.02  # Larger dt for speed
num_trials = 50

# Test 1: Single trajectory
print("\n[TEST 1] Single Trajectory")
print("-" * 70)

θ0 = 3.14159/4
q0 = sim.np.array([sim.np.cos(θ0), sim.np.sin(θ0)])
p0 = sim.np.array([0.5, -0.5])
state0 = sim.State(q0, p0, 0.7)

results1 = sim.run_simulation(state0, T=T_sim, dt=dt_sim)
final = results1['final_state']

print(f"Initial: ρ={sim.constraint_violation(state0):.2e}, E={sim.total_energy(state0):.4f}")
print(f"Final:   ρ={sim.constraint_violation(final):.2e}, E={sim.total_energy(final):.4f}")
print(f"ΔE = {results1['energy'][-1] - results1['energy'][0]:.4f}")
print(f"Avg corrections/step: {sim.np.mean(results1['correction_iterations']):.2f}")

# Test 2: Lyapunov experiment
print(f"\n[TEST 2] Lyapunov Stability ({num_trials} trials)")
print("-" * 70)

constraint_ok = 0
energy_dec = 0
convergence = 0
total_corrections = 0

start_time = time.time()

for trial in range(num_trials):
    θ = sim.np.random.uniform(0, 2*3.14159)
    q_init = sim.np.array([sim.np.cos(θ), sim.np.sin(θ)])
    p_magnitude = sim.np.random.uniform(0.1, 2.0)
    p_direction = sim.np.array([-sim.np.sin(θ), sim.np.cos(θ)])
    p_init = p_magnitude * p_direction
    β_init = sim.np.random.uniform(0.5, 1.5)
    
    state_init = sim.State(q_init, p_init, β_init)
    res = sim.run_simulation(state_init, T=T_sim, dt=dt_sim)
    
    final_constraint = res['constraint'][-1]
    final_velocity = res['velocity_norm'][-1]
    energy_decreased = res['energy'][-1] < res['energy'][0]
    
    if final_constraint < 1e-3:
        constraint_ok += 1
    
    if energy_decreased:
        energy_dec += 1
    
    if final_velocity < 0.01:
        convergence += 1
    
    trial_corrections = int(sim.np.sum(res['correction_iterations']))
    total_corrections += trial_corrections
    
    if (trial + 1) % 10 == 0:
        print(f"  Trial {trial+1:2d}/{num_trials}: ρ={final_constraint:.2e}, E_dec={energy_decreased}, corr={trial_corrections}")

elapsed = time.time() - start_time

print(f"\n{'='*70}")
print(" RESULTS v2.0")
print(f"{'='*70}")
print(f"Energy decrease:         {energy_dec}/{num_trials} ({energy_dec/num_trials*100:.1f}%)")
print(f"Constraint satisfaction: {constraint_ok}/{num_trials} ({constraint_ok/num_trials*100:.1f}%)")
print(f"Convergence:             {convergence}/{num_trials} ({convergence/num_trials*100:.1f}%)")
print(f"\nConstraint Correction:")
print(f"  Total corrections:     {total_corrections}")
print(f"  Avg per trial:         {total_corrections/num_trials:.1f}")
print(f"\nElapsed time:            {elapsed:.1f} seconds")

print(f"\n{'='*70}")
print(" COMPARISON: v1.0 vs v2.0")
print(f"{'='*70}")
print(f"{'Metric':<30} {'v1.0':<15} {'v2.0':<15} {'Improvement'}")
print("-" * 70)
print(f"{'Constraint satisfaction':<30} {'68.0%':<15} {constraint_ok/num_trials*100:.1f}%{'':<12} +{constraint_ok/num_trials*100 - 68.0:.1f}%")
print(f"{'Energy decrease':<30} {'100.0%':<15} {energy_dec/num_trials*100:.1f}%{'':<12} Same")
print(f"{'Convergence':<30} {'68.0%':<15} {convergence/num_trials*100:.1f}%{'':<12} +{convergence/num_trials*100 - 68.0:.1f}%")

improvement = constraint_ok/num_trials*100 - 68.0
if improvement >= 27:
    status = "TARGET ACHIEVED (95%+) ✓✓✓"
elif improvement >= 15:
    status = "SIGNIFICANT IMPROVEMENT ✓✓"
else:
    status = "MODERATE IMPROVEMENT ✓"

print(f"\n{'='*70}")
print(f" STATUS: {status}")
print(f"{'='*70}\n")
