"""
Hospital Price Transparency (Uofl health, Baptist Hospital, Norton Hospital)
"""

import os
import argparse
import numpy as np
import pandas as pd

OUTPUT_FILE = "hospital_charges_clean.csv"
REAL_HEADER_SENTINELS = {"description", "code|1"}

FINAL_COLS = [
    "hospital", "cpt_code","code_type",  "procedure_name", "description",
    "gross_charge", "cash_price","negotiated_rate", "min_negotiated", "max_negotiated",
    "payer_name", "plan_name",  "rate_exceeds_gross",
]

def parse_args():
    p = argparse.ArgumentParser(description="Clean CMS hospital price transparency CSV files")
    p.add_argument("--input",  nargs="+", required=True)
    p.add_argument("--output", default=OUTPUT_FILE)
    return p.parse_args()


def detect_layout(columns):
    if "payer_name" in columns:
        return "long"
    return "wide"

def clean_numeric(s):
    return (
        s.astype(str)
         .str.replace(r"[\$,\s]", "", regex=True)
         .replace({"nan": np.nan, "": np.nan, "None": np.nan})
         .pipe(pd.to_numeric, errors="coerce")
    )
# since there were different codes, set priority for the codes and extract the highest priority code from each row. 
# The priority is set as follows: CPT > HCPCS > NDC > RC > CDM. If none of these are found, it will return the value in slot 1 as a fallback.     

def extract_cpt(row):
    CODE_PRIORITY = ["CPT", "HCPCS", "NDC", "RC", "CDM"]

    found = {}  

    for i in range(1, 5):
        code_val  = str(row.get(f"code|{i}", "")).strip()
        code_type = str(row.get(f"code|{i}|type", "")).strip().upper()

        if code_val and code_val != "nan" and code_type and code_type != "NAN":
    
            if code_type not in found:
                found[code_type] = code_val

    #Return highest priority match
    for priority_type in CODE_PRIORITY:
        if priority_type in found:
            return found[priority_type], priority_type

    # Absolute fallback — whatever is in slot 1
    fallback_val  = str(row.get("code|1", "")).strip()
    fallback_type = str(row.get("code|1|type", "")).strip().upper()
    return (fallback_val if fallback_val != "nan" else None), \
           (fallback_type if fallback_type != "NAN" else "UNKNOWN")


def process_file(path):
    print(f"Processing: {os.path.basename(path)}")

    #Norton and Baptist have ragged meta rows, so we need to use the python engine to read the files. Uofl has no ragged rows so it can be read with the default engine.

    print("\n[Step 1] Loading raw file …")

    meta_raw  = pd.read_csv(path, header=None, dtype=str,
                             nrows=2, engine="python")
    row0_vals = {str(v).strip() for v in meta_raw.iloc[0] if pd.notna(v)}
    has_meta  = len(row0_vals & REAL_HEADER_SENTINELS) < 2  # row 0 is NOT real headers

    if has_meta:
        #meta rows present — real headers start at row 2
        data_raw = pd.read_csv(path, header=None, dtype=str,
                                skiprows=2, engine="python")
    else:
        #No meta rows — headers at row 0, data from row 1
        data_raw = pd.read_csv(path, header=None, dtype=str, engine="python")

    print(f"  Loaded: {data_raw.shape[0]} rows × {data_raw.shape[1]} columns")

    # Now this extracts hospital metadata 
    print("\n[Step 2] Extracting hospital metadata …")
    hospital_name = "Unknown Hospital"
    last_updated  = "N/A"

    if has_meta:
        meta_keys   = meta_raw.iloc[0].tolist()
        meta_values = meta_raw.iloc[1].tolist()
        meta = {
            str(k).strip(): str(v).strip()
            for k, v in zip(meta_keys, meta_values)
            if pd.notna(v) and str(v).strip() not in ("nan", "")
        }
        hospital_name = meta.get("hospital_name", "Unknown Hospital")
        last_updated  = meta.get("last_updated_on", "N/A")
    else:
        hospital_name = (
            os.path.splitext(os.path.basename(path))[0]
            .replace("_", " ").replace("-", " ").title()
        )
        print("  No metadata rows — name inferred from filename")

    print(f"  Hospital : {hospital_name}")
    print(f"  Updated  : {last_updated}")

    # Set real headers & isolate data rows
    real_headers = data_raw.iloc[0].tolist()
    df = data_raw.iloc[1:].copy()
    df.columns = real_headers
    df = df.reset_index(drop=True)
    print(f"  Data rows : {len(df)}")
    print(f"  Columns   : {len(df.columns)}")

    #Detect wide vs long
    layout = detect_layout(df.columns.tolist())
    print(f"\n[Step 4] Layout detected: {layout.upper()}")

   
  #Apply to every row
    code_results = df.apply(extract_cpt, axis=1)

    df["cpt_code"]  = code_results.apply(lambda x: x[0])  # the code value
    df["code_type"] = code_results.apply(lambda x: x[1])  # CPT / HCPCS / RC / CDM etc.
    if layout == "wide":
        df_out = process_wide(df, hospital_name)
    else:
        df_out = process_long(df, hospital_name)

#   final cleanup and reordering of columns to match the final output format.
    for col in FINAL_COLS:
        if col not in df_out.columns:
            df_out[col] = np.nan
    df_out = df_out[FINAL_COLS].copy()

    for col in ["hospital", "cpt_code", "procedure_name", "description",
                "payer_name", "plan_name", "rate_exceeds_gross"]:
        df_out[col] = df_out[col].astype(str).str.strip().replace("nan", np.nan)

    before  = len(df_out)
    df_out  = df_out.drop_duplicates()
    removed = before - len(df_out)
    if removed:
        print(f"  Removed {removed:,} duplicate rows")

    print(f"\n[Summary] {hospital_name}")
    print(f"  Output rows     : {len(df_out):,}")
    print(f"  Unique CPT codes: {df_out['cpt_code'].nunique()}")
    print(f"  Unique payers   : {df_out['payer_name'].nunique()}")

    return df_out


#WIDE layout processor 
def process_wide(df, hospital_name):
   
    print("\nWIDE Identifying payer columns and melting …")

    base_col_map = {
        "description"                    : "description",
        "standard_charge|gross"          : "gross_charge",
        "standard_charge|discounted_cash": "cash_price",
        "standard_charge|min"            : "min_negotiated",
        "standard_charge|max"            : "max_negotiated",
    }
    missing = [k for k in base_col_map if k not in df.columns]
    if missing:
        print(f"  WARNING: Missing base columns (will be NaN): {missing}")

    df_base = df[[c for c in base_col_map if c in df.columns] + ["cpt_code"]].rename(columns=base_col_map)
    for col in ["description", "gross_charge", "cash_price", "min_negotiated", "max_negotiated"]:
        if col not in df_base.columns:
            df_base[col] = np.nan
    df_base["procedure_name"] = df_base["description"]
    df_base["hospital"]       = hospital_name

    payer_cols = [
        c for c in df.columns
        if isinstance(c, str)
        and c.startswith("standard_charge|")
        and c.endswith("|negotiated_dollar")
    ]
    print(f"  Payer columns found: {len(payer_cols)}")

    df_payer        = df[payer_cols].copy()
    df_payer.index  = df_base.index
    df_melted       = df_payer.melt(ignore_index=False,
                                     var_name="payer_col",
                                     value_name="negotiated_rate")
    df_melted       = df_melted.reset_index().rename(columns={"index": "orig_idx"})

    parsed = df_melted["payer_col"].apply(
        lambda c: tuple(c.split("|")[1:3]) if len(c.split("|")) >= 3 else ("Unknown", "Unknown")
    )
    df_melted["payer_name"] = parsed.apply(lambda x: x[0])
    df_melted["plan_name"]  = parsed.apply(lambda x: x[1])

    df_base_idx             = df_base.copy()
    df_base_idx["orig_idx"] = df_base_idx.index
    df_out = df_melted.merge(df_base_idx, on="orig_idx", how="left")

    for col in ["gross_charge", "cash_price", "min_negotiated", "max_negotiated", "negotiated_rate"]:
        if col in df_out.columns:
            df_out[col] = clean_numeric(df_out[col])

    before = len(df_out)
    df_out = df_out[df_out["negotiated_rate"].notna()].copy()
    print(f"  Dropped {before - len(df_out):,} rows with no rate → {len(df_out):,} remaining")

    df_out["rate_exceeds_gross"] = (df_out["negotiated_rate"] > df_out["gross_charge"]).map({True: "Yes", False: "No"})
    df_out.loc[df_out["gross_charge"].isna(), "rate_exceeds_gross"] = "Unknown"

    return df_out


#LONG layout processor 
def process_long(df, hospital_name):
    """Long: one row per payer- rename columns."""
    print("\nLONG Renaming columns")

    col_map = {
        "description"                      : "description",
        "standard_charge|gross"            : "gross_charge",
        "standard_charge|discounted_cash"  : "cash_price",
        "standard_charge|min"              : "min_negotiated",
        "standard_charge|max"              : "max_negotiated",
        "payer_name"                       : "payer_name",
        "plan_name"                        : "plan_name",
        "standard_charge|negotiated_dollar": "negotiated_rate",
    }
    missing = [k for k in col_map if k not in df.columns]
    if missing:
        print(f" WARNING: Missing columns (will be NaN): {missing}")

    df_out = df[[c for c in col_map if c in df.columns]].rename(columns=col_map)
    for col in col_map.values():
        if col not in df_out.columns:
            df_out[col] = np.nan

    df_out["cpt_code"]       = df["cpt_code"].values
    df_out["procedure_name"] = df_out["description"]
    df_out["hospital"]       = hospital_name

    for col in ["gross_charge", "cash_price", "min_negotiated", "max_negotiated", "negotiated_rate"]:
        df_out[col] = clean_numeric(df_out[col])

    before = len(df_out)
    df_out = df_out[df_out["negotiated_rate"].notna()].copy()
    print(f"  Dropped {before - len(df_out):,} rows with no rate → {len(df_out):,} remaining")

    df_out["rate_exceeds_gross"] = (df_out["negotiated_rate"] > df_out["gross_charge"]).map({True: "Yes", False: "No"})
    df_out.loc[df_out["gross_charge"].isna(), "rate_exceeds_gross"] = "Unknown"

    return df_out


#MAIN
def main():
    args = parse_args()

    for path in args.input:
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}")
            continue
        df = process_file(path)

    df.to_csv(args.output, index=False)
    print(f"\n  Saved → {args.output}")
   


if __name__ == "__main__":
    main()


#Since the combined data was massive with too many procedures and cpts I decided to filter out and analyse selected CPTS so i combined the files in next script and filtered the data. The code is in the next script named: filter_combine.py
