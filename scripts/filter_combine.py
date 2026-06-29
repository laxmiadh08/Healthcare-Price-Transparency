# import pandas as pd
# folder = "../clean-data"

# # Read the three CSV files
# df1 = pd.read_csv(f"{folder}/clean_baptist.csv")
# df2 = pd.read_csv(f"{folder}/clean_norton.csv")
# df3 = pd.read_csv(f"{folder}/clean_uofl.csv")

# # Combine the three dataframes
# combined_df = pd.concat([df1, df2, df3], ignore_index=True)
# # combined_df.to_csv(f"{folder}/combined_data.csv", index=False)
# # # CPT codes to keep
# cpt_codes = [
#     "70553", "70551", "72148", "72193", "74177", "70450", "76700",
#     "76830", "73721", "71260", "73221", "74160", "45378", "45385",
#     "43239", "29881", "29827", "66984", "52000", "95810", "93000",
#     "93306", "80053", "80061", "80069", "85025", "83735", "84443",
#     "93451", "94060", "470", "291", "392", "603", "871", "872",
#     "193", "292", "310", "641", "690", "795", "775", "765",
#     "58150", "58558", "99283", "99284", "99285", "99214"
# ]

# # # Convert CPT column to string (important)
# combined_df["code"] = combined_df["code"].astype(str).str.strip()

# # # Filter
# filtered_df = combined_df[combined_df["code"].isin(cpt_codes)]

# # Export
# filtered_df.to_csv("filtered_data.csv", index=False)

# # print(filtered_df.shape)



import pandas as pd

folder = "../clean-data"

# Read the three CSV files
df1 = pd.read_csv(
    f"{folder}/clean_baptist.csv",
    dtype={"cpt_code": str},
    low_memory=False
)

df2 = pd.read_csv(
    f"{folder}/clean_norton.csv",
    dtype={"cpt_code": str},
    low_memory=False
)

df3 = pd.read_csv(
    f"{folder}/clean_uofl.csv",
    dtype={"cpt_code": str},
    low_memory=False
)

# Combine the three dataframes
combined_df = pd.concat([df1, df2, df3], ignore_index=True)

print(f"Combined rows: {len(combined_df):,}")

# CPT codes to keep
cpt_codes = [
    "70553", "70551", "72148", "72193", "74177", "70450", "76700",
    "76830", "73721", "71260", "73221", "74160", "45378", "45385",
    "43239", "29881", "29827", "66984", "52000", "95810", "93000",
    "93306", "80053", "80061", "80069", "85025", "83735", "84443",
    "93451", "94060", "470", "291", "392", "603", "871", "872",
    "193", "292", "310", "641", "690", "795", "775", "765",
    "58150", "58558", "99283", "99284", "99285", "99214"
]

# Clean CPT codes
combined_df["cpt_code"] = (
    combined_df["cpt_code"]
    .astype(str)
    .str.strip()
    .str.replace(".0", "", regex=False)
)

# Filter
filtered_df = combined_df[
    combined_df["cpt_code"].isin(cpt_codes)
]

print(f"Filtered rows: {len(filtered_df):,}")

# Export
filtered_df.to_csv(f"{folder}/filtered_data.csv", index=False)

print("Done!")