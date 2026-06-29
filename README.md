## Healthcare Price Transparency
Analyzed 6K rows data by filtering 49 CPT codes from a dataset with 7,230,075 rows from CMS Healthcare transparency data for three hospitals in Louisville

## Data Source: CMS 
- Hospitals (all three are from Louisville): Uofl Health, Baptist Health, Norton Hospital
---
Target combined output file will contain following columns:
hospital | cpt_code | procedure_name | description| gross_charge | cash_price | min_negotiated | max_negotiated | payer_name | plan_name | negotiated_rate | rate_exceeds_gross

## Data exploration

The files were large and in Machine Readable Format (MRF) hence the cleanup and getting them ready to combine took longer than anticipitaed
To get a quick view I imported the files in jupyter notebook and exported first 100 rows for all three files, which helped me view the files and evaulate the data.
File info: 
UOFL: 1.16GB | Rows: 239368 | Columns: 379
BAPTIST: 254 MB | Rows: 775240| Columns: 28
NORTON: 2.17GB | Rows: | Columns:


-----
## Data cleaning and processing 

UofL file format:
    Row 0: meta keys   (hospital_name, last_updated_on …)
    Row 1: meta values (University Medical Center …)
    Row 2: real headers (description, code|1 … + one column per payer)
    Row 3 onwards: procedure data 

 Norton Hospital and Baptist Hospital file format:
    Row 0: meta keys
    Row 1: meta values  ← these rows have FEWER columns than data rows
    Row 2: real headers (description, code|1, payer_name, plan_name, standard_charge|negotiated_dollar …)
    Row 3 onwards: one row per procedure x payer 

Uofl dataset was in wide format and needed to pivot the table to combine the procedure with payers to create a production ready format.
(link the column info)
Note: I used LLM to identify the wide format and  consolidate these columns.
- each payer had its own column, I Identified that each payer has its own column.
- steps involved
    - Find all payers column staring standard_charge and ended with negoitated_dollar and unpivot these columns into rows.


The combined file had rows: 7,230,075
For the purpose of this analyis i filterd and kept only these CPT codes
and new dataset rows: 6,681
CPT codes picked for this analysis are:
[
  "70553", "70551", "72148", "72193", "74177", "70450", "76700",
    "76830", "73721", "71260", "73221", "74160", "45378", "45385",
    "43239", "29881", "29827", "66984", "52000", "95810", "93000",
    "93306", "80053", "80061", "80069", "85025", "83735", "84443",
    "93451", "94060", "470", "291", "392", "603", "871", "872",
    "193", "292", "310", "641", "690", "795", "775", "765",
    "58150", "58558", "99283", "99284", "99285", "99214"
]

Code,Procedure Name
70553,"MRI scan of brain, before and after contrast dye"
70551,"MRI scan of brain, without contrast dye"
72148,"MRI scan of lumbar spine (lower back), without contrast dye"
72193,"CT scan of pelvis, with contrast dye"
74177,"CT scan of abdomen and pelvis, with contrast dye"
70450,"CT scan of head or brain, without contrast dye"
76700,"Ultrasound of abdomen, complete evaluation"
76830,"Ultrasound of transvaginal pelvis"
73721,"MRI scan of lower extremity joint (e.g., knee, ankle), without contrast"
71260,"CT scan of thorax (chest), with contrast dye"
73221,"MRI scan of upper extremity joint (e.g., shoulder, wrist), without contrast"
74160,"CT scan of abdomen, with contrast dye"
45378,"Diagnostic colonoscopy, flexible"
45385,"Colonoscopy with removal of polyps or growths via snare technique"
43239,"Upper GI endoscopy (EGD) with biopsy of tissue"
29881,"Knee arthroscopy with surgical cartilage removal (meniscectomy)"
29827,"Shoulder arthroscopy with rotator cuff repair"
66984,"Cataract surgery with intraocular lens insertion, manual"
52000,"Cystourethroscopy (visual testing of the bladder)"
95810,"Polysomnography (sleep study) for patients 6 years or older"
93000,"Routine Electrocardiogram (ECG/EKG) with interpretation and report"
93306,"Echocardiography (ultrasound of the heart), transthoracic"
80053,"Comprehensive metabolic panel (blood chemistry test)"
80061,"Lipid panel (cholesterol and triglycerides test)"
80069,"Kidney (renal) function blood test panel"
85025,"Complete blood count (CBC) with automated differential"
83735,"Magnesium blood test"
84443,"Thyroid stimulating hormone (TSH) blood test"
93451,"Right heart catheterization (cardiac function testing)"
94060,"Bronchospasm evaluation (spirometry/breathing test before and after bronchodilator)"
470,"Major hip and knee joint replacement or lower extremity reattachment without MCC (Major Complications)"
291,"Heart failure and shock with MCC"
392,"Esophagitis, gastroenteritis, and miscellaneous digestive disorders without MCC"
603,"Cellulitis (skin infection) without MCC"
871,"Septicemia or severe sepsis without mechanical ventilation >96 hours with MCC"
872,"Septicemia or severe sepsis without mechanical ventilation >96 hours without MCC"
193,"Simple pneumonia and pleurisy with MCC"
292,"Heart failure and shock with CC (Complications)"
310,"Cardiac arrhythmia and conduction disorders without CC/MCC"
641,"Nutritional and miscellaneous metabolic disorders without MCC"
690,"Kidney and urinary tract infections without MCC"
795,"Normal newborn delivery"
775,"Vaginal delivery without complicating diagnoses"
765,"Cesarean section delivery with CC/MCC"
58150,"Total abdominal hysterectomy"
58558,"Hysteroscopy with surgical biopsy or polyp removal"
99283,"Emergency department visit, level 3 (Moderate severity)"
99284,"Emergency department visit, level 4 (High severity without immediate threat)"
99285,"Emergency department visit, level 5 (High severity with immediate life/physiologic threat)"
99214,"Office or outpatient clinic visit for the evaluation/management of an established patient, 30–39 minutes"


## Next step I imported the file in PowerBI
## Business Questions:
Pricing Transparency & Fairness

1. Which hospital charges the highest gross charge for the same CPT code — and how does their negotiated rate compare?
2. For which procedures does the negotiated rate exceed the gross charge — and which payers are involved?
3. How wide is the pricing spread (max vs min negotiated) for the same procedure across payers at each hospital?

Payer & Plan Analysis

4. Which payer consistently negotiates the lowest rates across all procedures?

5. Which plan type (Medicare Advantage, Commercial, Managed Medicaid) gets the best discount off gross charge?

6. Which hospital gives the deepest discount to cash-paying patients vs their best negotiated payer rate?
Procedure-Level Insights

7. Which CPT codes show the largest dollar difference in negotiated rates between hospitals — for the same payer?

8. Which procedures have the most negotiating variability (highest standard deviation in negotiated rate)?

9. How does each hospital's cash price compare to their lowest negotiated rate — is cash ever cheaper?
Hospital Competitiveness

10. Which hospital is the most expensive overall and which is most affordable — by median negotiated rate?





Created a data model (star schema)




Using DAX, calculated the KPI and metrics
