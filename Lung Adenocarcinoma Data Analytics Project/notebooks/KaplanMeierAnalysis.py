from lifelines import KaplanMeierFitter
import pandas as pd

df = pd.read_csv("data_clean/luad_analytics_dataset.csv")  # Assuming this CSV has 'survival_time', 'event', and 'stage' columns

kmf = KaplanMeierFitter()

results = []

for stage in df['stage'].unique():
    stage_df = df[df['stage'] == stage]
    
    kmf.fit(
        durations=stage_df['overall_survival_months'],
        event_observed=stage_df['event'],
        label=stage
    )
    
    temp = kmf.survival_function_.reset_index()
    
    # Rename columns properly
    temp.columns = ['time', 'survival_prob']
    
    # Add stage column
    temp['stage'] = stage
    
    results.append(temp)

# Combine everything
final_km = pd.concat(results)

# Save ONE clean file
final_km.to_csv("km_by_stage.csv", index=False)
final_km.to_csv("km_by_stage.csv", index=False)