# Aashu Jewellers — Silver Manufacturing Management System

## 🏢 About

Professional desktop ERP application for **Aashu Jewellers** to manage:
- Silver issued to Karigars (artisans/makers)
- Silver received back from Karigars
- Advance money tracking
- Labour & scrap weight calculation
- Monthly ledger reports
- Database backups

## 🛠 Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| UI Framework | CustomTkinter |
| Database | Microsoft Access (.accdb) |
| Reports | ReportLab (PDF) + openpyxl (Excel) |
| Architecture | Clean Architecture + MVVM + Repository Pattern |

## 📦 Installation

### Prerequisites

1. **Python 3.11+** — [Download](https://www.python.org/downloads/)
2. **Microsoft Access Database Engine** — [Download](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
   - Must match Python bitness (32-bit or 64-bit)

### Setup

```bash
# Navigate to project folder
cd "e:\dukan app"

# Install dependencies
py -m pip install -r requirements.txt

# Run the application
py main.py
```

## 🚀 Running

```bash
py main.py
```

The application will:
1. Create required directories
2. Create the Access database (if not exists)
3. Initialize all tables and indexes
4. Seed default item types and settings
5. Launch the GUI

## 📁 Project Structure

```
├── main.py                # Entry point
├── config/                # App & database configuration
├── database/              # Connection, schema, seed data
├── models/                # Domain models (dataclasses)
├── repositories/          # Data access layer (CRUD)
├── services/              # Business logic layer
├── viewmodels/            # MVVM state management
├── views/
│   ├── app.py             # Main window + sidebar
│   ├── components/        # Reusable UI widgets
│   ├── pages/             # Application pages
│   └── dialogs/           # Modal dialogs
├── utils/                 # Helpers, validators, theme
├── assets/                # Icons, fonts, logo
├── data/                  # Database file
├── backups/               # Monthly backups
└── reports/generated/     # PDF/Excel reports
```

## 🎯 Features

### Core Modules
- **Dashboard** — Stats, quick navigation
- **Issue Entry** — Record silver issued to Karigars
- **Receive Entry** — Record silver received (auto-calc scrap/net weight)
- **Karigar Management** — Full CRUD with activate/deactivate
- **Item Type Management** — Configurable item categories
- **Search** — Multi-criteria search across all entries
- **Reports** — 4 report types with PDF/Excel export
- **Backup** — Monthly database backup and restore
- **Settings** — Company info, theme, paths

### Business Logic
| Calculation | Formula |
|---|---|
| Scrap Weight | Gross Weight − Labour Weight |
| Net Weight | Gross Weight − Scrap Weight |
| Pending Silver | Total Issued − Total Received |
| Status | "Naam" if Pending > 0, "Jama" otherwise |

### Reports
1. **Individual Karigar Ledger** — Running balance per Karigar
2. **All Karigars Summary** — One row per Karigar
3. **Date Wise Report** — Entries between dates
4. **Monthly Summary** — Monthly totals

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+N` | New Entry / Clear Form |
| `Ctrl+S` | Save / Add Entry |
| `Ctrl+U` | Update Selected Entry |
| `Delete` | Delete Selected Entry |
| `Enter` | Navigate to next field / Submit Form |
| `Alt+H` | Go to Dashboard |
| `Alt+F4` | Exit |

## 🏗️ Building Executable (Windows App)

To convert this Python application into a standalone Windows `.exe` application, you can use **PyInstaller**. We have provided a pre-configured `AashuJewellers.spec` file that includes all assets, database folders, and the application icon.

### 1. Install PyInstaller
```bash
py -m pip install pyinstaller
```

### 2. Build the Application
Run the following command from the project root. This command uses the spec file to package the app as a windowed Windows application (without console):

```bash
py -m PyInstaller AashuJewellers.spec
```

Alternatively, to build it manually as a single windowed `.exe` file without the spec file, you can run:

```bash
py -m PyInstaller --noconsole --onefile --windowed --icon="assets\icons\app_icon.ico" main.py
```

*(Note: Building with the `.spec` file is recommended as it correctly includes all required assets, folders, and CustomTkinter dependencies.)*

### 3. Distribute
Once the build is complete:
- A `dist` folder will be created in your project directory.
- Inside `dist\AashuJewellers`, you will find `AashuJewellers.exe`.
- You can copy this entire `AashuJewellers` folder to any Windows machine.
- *Note: The target machine must still have the Microsoft Access Database Engine installed to connect to the `.accdb` file.*

## 🔗 Creating a Desktop Shortcut

**If running from the built Executable (`.exe`):**
1. Navigate to the `dist\AashuJewellers` folder.
2. Right-click on `AashuJewellers.exe`.
3. Select **Send to** > **Desktop (create shortcut)**.
4. The shortcut will appear on your desktop with the app's beautiful icon.

**If running directly from Python (`main.py`):**
1. Right-click on your Desktop and select **New** > **Shortcut**.
2. Enter `python "C:\path\to\your\project\main.py"` (Update the path to wherever the app is located, e.g., `python "e:\dukan app\main.py"`).
3. Name it "Aashu Jewellers".
4. To set the icon: Right-click the shortcut > **Properties** > **Change Icon...** > **Browse** to `assets\icons\app_icon.ico` and apply.

## 📋 License

© 2024 Aashu Jewellers. All rights reserved.
