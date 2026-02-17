# xrinex

**xrinex** is a Python toolkit for reading and processing **RINEX (Receiver Independent Exchange Format)** and **SP3 (Standard Precision Orbit)** files.

It provides utilities to extract GNSS observables such as:

* Pseudorange (C1, P2, etc.)
* Carrier phase (L1, L2)
* LLI / SSI flags
* Satellite positions from SP3 files
* Orbit interpolation
* Multi-indexed GNSS datasets (time, PRN)

The library is designed for scientific GNSS data analysis and ionospheric research workflows.

---

## ✨ Features

* Read **RINEX 2 observation files**
* Parse GNSS observables into structured `pandas` DataFrames
* Read **SP3 precise orbit files**
* Interpolate satellite coordinates
* MultiIndex output format: `(time, prn)`
* Compatible with zipped RINEX files
* Designed for TEC / ROTI / ionospheric analysis pipelines

---

## 📦 Installation

Install via pip:

```bash
pip install xrinex
```

Or install from source:

```bash
git clone https://github.com/your-username/xrinex.git
cd xrinex
pip install -e .
```

---

## 🔧 Requirements

* Python ≥ 3.9
* NumPy
* Pandas
* SciPy

Install dependencies manually if needed:

```bash
pip install numpy pandas scipy
```

---

## 🚀 Basic Usage

### Reading a RINEX 2 observation file

```python
import xrinex as xr

rinex = xr.Rinex2("example.10o")

# Get full dataset
df = rinex.dataset()

# List available PRNs
print(rinex.prns)

# Select data for one satellite
g02 = rinex.sel("G02")
```

Output format:

```
time                 L1        C1        L2        P2
2010-01-01 00:00:00  ...
```

---

### Reading SP3 orbit files

```python
import xrinex as xr

df = xr.mgex("igs12345.sp3")

print(df.head())
```

Output (MultiIndex):

```
time                 prn   x        y        z        clock
2010-01-01 00:00:00  G01   ...
```

---

## 📁 Project Structure

```
xrinex/
│
├── rinex2/         # RINEX 2 reader
├── sp3/            # SP3 orbit reader
├── utils/          # Helper utilities
└── ...
```

---

## 🧪 Supported Formats

* RINEX 2.xx (Observation files)
* SP3 (Precise orbit files)
* Compressed files (.zip, .gz, .Z) when supported

---

## 🎯 Use Cases

* Ionospheric TEC computation
* ROT / ROTI calculation
* Cycle slip detection
* Satellite orbit interpolation
* GNSS research pipelines
* Geomagnetic / space weather studies

---

## 🤝 Contributing

Contributions are welcome!

If you would like to:

* Report a bug
* Suggest improvements
* Add support for RINEX 3
* Improve performance

Please open an issue or submit a pull request.

---

## 📜 License

Add your license here (e.g., MIT License).

---

If you'd like, I can also:

* Make a **more academic-style README**
* Make a **PyPI-ready README**
* Add **badges (build, license, Python version)**
* Write a **proper `setup.py` or `pyproject.toml`**
* Add documentation section with examples for TEC/ROTI workflows**

Just tell me which direction you want 🚀
