import pandas as pd

# Load Final_Data_PV_Clear.csv
final_data_path = "Final_Data_PV_Clear.csv"
df_final = pd.read_csv(final_data_path, parse_dates=["TmStamp"])

# Copy 'TmStamp' values
tmstamp_values = df_final['TmStamp'].copy()

# Load Stage4.csv
stage4_path = "Load Shedding/Stage4.csv"
df_stage4 = pd.read_csv(stage4_path, parse_dates=["Timestamp"])

# Merge the two DataFrames on the timestamp columns
merged_df = df_final.merge(df_stage4, left_on="TmStamp", right_on="Timestamp", how="left")

# Drop the duplicate timestamp column (Timestamp) if needed
merged_df = merged_df.drop("Timestamp", axis=1)

# Reorder the columns as needed
column_order = [
    'TmStamp', 'Date', 'Time', 'TrackerWM_Avg', 'Tracker2WM_Avg', 'ShadowWM_Avg', 'SunWM_Avg',
    'ShadowbandWM_Avg', 'DNICalc_Avg', 'AirTC_Avg', 'RH', 'WS_ms_S_WVT', 'WindDir_D1_WVT',
    'WindDir_SD1_WVT', 'BP_mB_Avg', 'UVA_Avg', 'UVB_Avg', 'Weekday', 'Season', 'Total',
    'Stove', 'Lights and Pool', 'Geyser', 'Plugs', 'Total E', 'Stove E', 'Lights and Pool E',
    'Geyser E', 'Plugs E', 'p_dc_m', 'Loadshedding'
]

merged_df = merged_df[column_order]

# Save the merged DataFrame to Final_Data_PV_Clear_Loadshedding.csv
merged_df.to_csv("Final_Data_PV_Clear_Loadshedding.csv", index=False)