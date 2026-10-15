# Lab 4: replication starter kit

The assignment is in [`reading-materials/Lab4-Paper-Replication-Assignment.md`](../../reading-materials/Lab4-Paper-Replication-Assignment.md).

```powershell
.\get-data.ps1                          # downloads and checks Card & Krueger's public files into data\
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe starter.py data\public.dat
```

| File | For |
|---|---|
| `get-data.ps1` | Downloads `njmin.zip` (data, codebook, original SAS program) and checks it against the tested version |
| `requirements.txt` | Pinned NumPy and pandas, tested with Python 3.12.14 |
| `starter.py` | Participant scaffold with the tasks as TODOs |
| `facilitator/reference_solution.py` | Full replication. Exits with an error unless all five Table 4 entries match. Run: `python -I facilitator/reference_solution.py data/public.dat` |
