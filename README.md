
# Inequality Inertia Simulator

A small Streamlit app to illustrate how systemic bias creates persistent inequality unless corrective interventions are applied—and how/when to taper those interventions.

## Quick start

1. Create a virtual environment (recommended), then install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run app.py
   ```

3. In the sidebar, set **Bias (beta)** > 0 and **Intervention (tau)** = 0 to see persistent inequality (two bubbles at different heights).
   Increase **tau** or switch to **Quota** to move toward parity. Toggle **Auto-taper tau** to explore when to stop positive discrimination without re-segregation.

## Model sketch

- Selection weights: exp(k*capital) * bias * intervention
- Feedback: capital += alpha*1[P] + gamma*mean(capital of P) + noise
- Policies: weighted (soft) or quota (hard min share)
- Parity checks: representation, conditional selection parity, capital gap

## Notes

This is a didactic prototype. You can expand it to:
- multiple intersecting subgroups,
- chained gates (education -> job -> leadership),
- empirical calibration with real data.
