import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# =============== Simulation Function ==================
def run_simulation(
    N=800,
    pop_share_B=0.3,
    beta=0.3,
    tau=0.0,
    alpha=0.4,
    gamma=0.15,
    capacity_P=150,
    turnover_rate=0.1,
    rA=0.95,
    rB=0.92,
    T=400,
    policy="weighted",
    quota_min_B_share=0.5,
    k=0.5,
    noise_sd=0.0,
    seed=0,
):
    rng = np.random.default_rng(seed)

    # Assign groups
    group_B = rng.random(N) < pop_share_B
    z = np.zeros(N, dtype=bool)      # Power tier membership
    c = rng.normal(0, 1, size=N)     # Capital

    def safe_log(x):
        return np.log(np.maximum(x, 1e-12))

    for t in range(T):
        # ---- Exits (retention) ----
        exit_prob = np.where(group_B, 1 - rB, 1 - rA)
        leaving_retention = z & (rng.random(N) < exit_prob)
        z[leaving_retention] = False

        # ---- Extra turnover ----
        if turnover_rate > 0:
            inP_idx = np.where(z)[0]
            n_turnover = int(np.round(turnover_rate * len(inP_idx)))
            if n_turnover > 0:
                drop_idx = rng.choice(inP_idx, size=n_turnover, replace=False)
                z[drop_idx] = False

        # ---- Openings (respect capacity) ----
        current_inP = int(z.sum())
        openings = max(0, capacity_P - current_inP)

        # Guarantee some churn so the bubble can move (8% of capacity each step)
        min_open = max(1, int(0.08 * capacity_P))
        openings = max(openings, min_open)

        # ---- Selection ----
        if openings > 0:
            candidates = np.where(~z)[0]
            if len(candidates) > 0:
                caps = c[candidates]

                # base score
                score = k * caps
                score += np.where(group_B[candidates], safe_log(1 - beta), safe_log(1 + beta))

                if policy == "weighted":
                    score += np.where(group_B[candidates], safe_log(1 + tau), 0.0)
                    n_pick = min(openings, len(candidates))
                    chosen = candidates[np.argsort(score)][-n_pick:]
                elif policy == "quota":
                    n_pick = min(openings, len(candidates))
                    prelim = candidates[np.argsort(score)][-n_pick:]
                    chosen = prelim.copy()

                    # Enforce minimum B share among the openings
                    B_mask = group_B[prelim]
                    current_B_count = int(B_mask.sum())
                    target_B_count = int(np.ceil(quota_min_B_share * n_pick))
                    if current_B_count < target_B_count:
                        needed = target_B_count - current_B_count
                        pool_B = candidates[group_B[candidates]]
                        extra_B = pool_B[~np.isin(pool_B, prelim)]
                        if len(extra_B) > 0:
                            add_B = rng.choice(extra_B, size=min(needed, len(extra_B)), replace=False)
                            # replace the lowest-scoring As
                            A_idx = np.where(~group_B[chosen])[0]
                            if len(A_idx) > 0:
                                chosen_scores = k * c[chosen] + np.where(group_B[chosen], safe_log(1 - beta), safe_log(1 + beta))
                                order_A = A_idx[np.argsort(chosen_scores[A_idx])]  # lowest first
                                to_replace = min(len(add_B), len(order_A))
                                if to_replace > 0:
                                    chosen[order_A[:to_replace]] = add_B[:to_replace]
                else:
                    n_pick = min(openings, len(candidates))
                    chosen = rng.choice(candidates, size=n_pick, replace=False)

                z[chosen] = True

        # ---- Capital update ----
        c += alpha * z + gamma * rng.normal(0, 1, size=N) + noise_sd * rng.normal(0, 1, size=N)
        c = np.clip(c, -12.0, 12.0)

    # Final representation (at step T-1)
    rep_B_final = float(group_B[z].mean()) if z.any() else 0.0
    return rep_B_final

# =============== Streamlit UI ==================
st.set_page_config(layout="wide", page_title="Inequity Inertia — Bubbles Only")

st.title("Inequity Inertia — Bubble View")
st.caption("The bubble’s x-axis is Group B’s population share. The y-axis is Group B’s share inside the power tier P after T steps.")

# Sidebar parameters
with st.sidebar:
    st.header("Parameters")
    N = st.slider("Population size", 100, 2000, 800, step=50)
    pop_share_B = st.slider("Population share of Group B (x)", 0.0, 1.0, 0.3, step=0.01)
    beta = st.slider("Bias β (A-favoring)", 0.0, 1.0, 0.3, step=0.01)
    tau = st.slider("Intervention τ (Weighted only)", 0.0, 2.0, 0.0, step=0.01)
    alpha = st.slider("Capital gain α (if in P)", 0.0, 1.0, 0.4, step=0.01)
    gamma = st.slider("Random capital change γ", 0.0, 1.0, 0.15, step=0.01)
    capacity_P = st.slider("Capacity of P", 10, 2000, 150, step=10)
    turnover_rate = st.slider("Turnover rate", 0.0, 0.5, 0.1, step=0.01)
    rA = st.slider("Retention rA (Group A)", 0.0, 1.0, 0.95, step=0.01)
    rB = st.slider("Retention rB (Group B)", 0.0, 1.0, 0.92, step=0.01)
    T = st.slider("Steps (discrete cycles)", 10, 2000, 600, step=10)
    policy = st.selectbox("Policy", ["weighted", "quota"])
    quota_min_B_share = st.slider("Quota min B share (quota mode)", 0.0, 1.0, 0.5, step=0.01)
    k = st.slider("Capital weight k", 0.0, 2.0, 0.5, step=0.01)
    noise_sd = st.slider("Extra noise in capital", 0.0, 1.0, 0.0, step=0.01)
    seed = st.number_input("Random seed", 0, 9999, 0)
    st.markdown("---")
    show_parity = st.checkbox("Show parity diagonal (y = x)", value=False)

# Run simulation once (we only need the final point)
rep_B_T = run_simulation(
    N=N, pop_share_B=pop_share_B, beta=beta, tau=tau, alpha=alpha, gamma=gamma,
    capacity_P=capacity_P, turnover_rate=turnover_rate, rA=rA, rB=rB, T=T,
    policy=policy, quota_min_B_share=quota_min_B_share, k=k, noise_sd=noise_sd, seed=int(seed),
)

# Build bubble dataset (A & B bubbles)
bubbles_df = pd.DataFrame({
    "Group": ["A", "B"],
    "Population share (x)": [1.0 - pop_share_B, pop_share_B],
    "Share in P (y)": [1.0 - rep_B_T, rep_B_T]
})

# Optional parity diagonal (y = x)
layers = []
if show_parity:
    diag_df = pd.DataFrame({"x": [0.0, 1.0], "y": [0.0, 1.0]})
    diag = alt.Chart(diag_df).mark_line(strokeDash=[6, 4], color="gray").encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 1])),
    )
    layers.append(diag)

# Bubbles layer
bubbles = alt.Chart(bubbles_df).mark_circle(size=3000, opacity=0.8).encode(
    x=alt.X("Population share (x):Q", title="Population share of B (x)", scale=alt.Scale(domain=[0, 1])),
    y=alt.Y("Share in P (y):Q", title="Share of B inside P (y)", scale=alt.Scale(domain=[0, 1])),
    color=alt.Color("Group:N", scale=alt.Scale(domain=["A", "B"], range=["#1f77b4", "#ff7f0e"])),
    tooltip=[
        alt.Tooltip("Group:N"),
        alt.Tooltip("Population share (x):Q", format=".2f"),
        alt.Tooltip("Share in P (y):Q", format=".2f"),
    ],
).properties(height=620, width=820, title="Bubbles: Representation vs Population (final state)")

layers.append(bubbles)
bubble_chart = alt.layer(*layers)

# Center the single chart
st.empty()  # spacer
st.altair_chart(bubble_chart, use_container_width=False)
st.empty()  # spacer

# Metrics under the chart
st.markdown("### Metrics")
st.metric("B share in P (y)", f"{rep_B_T:.2%}")
st.metric("Population share of B (x)", f"{pop_share_B:.2%}")
st.metric("Representation gap (y − x)", f"{(rep_B_T - pop_share_B):.2%}")

st.caption(
    "Move the sliders to explore scenarios. "
    "Parity means the B bubble sits on the diagonal (y = x), i.e., representation equals population share."
)
