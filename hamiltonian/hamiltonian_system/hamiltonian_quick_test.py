# Quick test with dt=0.02, trials=10
import sys
sys.path.insert(0, '/home/user')

# Override parameters
import hamiltonian_sim_v2 as sim
sim.CONSTRAINT_TOLERANCE = 1e-5  # Relax tolerance for speed

# Test 1: Single trajectory
print("="*70)
print("QUICK TEST v2.0 (dt=0.02, T=20)")
print("="*70)

θ0 = 3.14159/4
q0 = [0.707, 0.707]
p0 = [0.5, -0.5]
state0 = sim.State(sim.np.array(q0), sim.np.array(p0), 0.7)

print(f"\nInitial constraint violation: {sim.constraint_violation(state0):.2e}")

results = sim.run_simulation(state0, T=20.0, dt=0.02)

print(f"Final constraint violation: {sim.constraint_violation(results['final_state']):.2e}")
print(f"Avg corrections per step: {sim.np.mean(results['correction_iterations']):.2f}")
print(f"Max constraint residual: {sim.np.max(results['correction_residuals']):.2e}")
print(f"Energy decreased: {results['energy'][-1] < results['energy'][0]}")

# Lyapunov test (10 trials only)
print("\n" + "="*70)
print("LYAPUNOV TEST (10 trials)")
print("="*70)

constraint_ok = 0
for i in range(10):
    θ = sim.np.random.uniform(0, 2*3.14159)
    q_init = sim.np.array([sim.np.cos(θ), sim.np.sin(θ)])
    p_init = sim.np.random.uniform(0.1, 2.0) * sim.np.array([-sim.np.sin(θ), sim.np.cos(θ)])
    β_init = sim.np.random.uniform(0.5, 1.5)
    
    state_init = sim.State(q_init, p_init, β_init)
    res = sim.run_simulation(state_init, T=20.0, dt=0.02)
    
    if res['constraint'][-1] < 1e-3:
        constraint_ok += 1
    
    print(f"  Trial {i+1:2d}: ρ_final={res['constraint'][-1]:.2e}, corrections={int(sim.np.sum(res['correction_iterations']))}")

print(f"\nConstraint satisfaction: {constraint_ok}/10 ({constraint_ok*10}%)")
print("\n" + "="*70)
