

---

## Overview

A professional desktop application built to replace the Excel-based FAT tracking system.
Centralized data, fast search, attachment management, and role-based access — all in one place.
---
![alt text](banner.png)
---

## Features

| Module | Description |
|--------|-------------|
| 📋 **FAT Records** | Add, edit, search, filter, and duplicate inspection records |
| 🏗️ **Projects** | Manage projects with full lifecycle tracking |
| 🏭 **Suppliers** | Supplier profiles with per-project contact assignments |
| 👔 **Consultants** | Consultant companies with engineer contacts per project |
| 📎 **Attachments** | Drag & drop upload — PDF, DOCX, XLSX, MSG, images, ZIP |
| 📊 **Dashboard** | Live charts — monthly trends, status breakdown, top suppliers |
| 📄 **Reports** | Excel export|
| ⚙️ **Settings** | User management, roles, password change, database path |

---

## Tech Stack

```
UI          PyQt6 + PyQt6-Charts
Database    SQLite (WAL mode — network share safe)
ORM         SQLAlchemy 2.0
Auth        bcrypt password hashing
Export      OpenPyXL
Packaging   PyInstaller → Setup.exe
```

---

## Architecture

```
UI Layer  (PyQt6)
    │
    ▼
Service Layer  (business logic)
    │
    ▼
Repository Layer  (data access)
    │
    ▼
SQLite Database  (fat_system.db)
```

UI never communicates with the database directly.  
Every operation passes through the service layer.

---

## Database

8 tables — fully relational with foreign key constraints.

```
projects
suppliers           ← one supplier, different contacts per project
supplier_contacts
consultants
consultant_contacts
fat_records         ← core table
attachments
users
audit_logs
```

**FAT record links to:**  project · supplier · supplier engineer · consultant · consultant engineer

---

## Getting Started

**1 — Install dependencies**

```bash
pip install -r requirements.txt
```

**2 — Migrate existing Excel data**

```bash
python migrations/migrate_from_excel.py --excel "FAT___INSPECTION.xlsx"
```

**3 — Run**

```bash
python main.py
```

Default credentials → `admin / admin123`  
Change the password immediately from **Settings → Change Password**.

---

## Build Setup.exe

```bash
# Step 1 — build the executable
python build.py

# Step 2 — open in Inno Setup and press F9
installer/setup.iss
```

Output: `installer/FAT_System_Setup_v1.0.0.exe`

---

## Network Deployment

The application is designed for a single writer with multiple read-only clients on a shared network drive.

```
Each machine  →  C:\Program Files\FAT_System\  (local install)
                          ↓  connects to
Company server  →  V:\Fat Test (Infra - HUB)\DB\fat_system.db
```

SQLite WAL mode is enabled — concurrent readers never block each other.  
The database path is configurable per machine via **Login → ⚙️ Change** without touching source code.

---

## File Storage

```
V:\Fat Test (Infra - HUB)\DB\
├── fat_system.db
├── attachments\
│   ├── reports\
│   ├── references\
│   ├── emails\
│   ├── photos\
│   └── drawings\
└── backups\
```

Files are never stored inside the database — only metadata and relative paths.

---

## User Roles

| Permission | Admin | Engineer |
|------------|:-----:|:--------:|
| Add / Edit FAT Records | ✓ | ✓ |
| Upload Attachments | ✓ | ✓ |
| Export Reports | ✓ | ✓ |
| Delete Records | ✓ | — |
| Manage Users | ✓ | — |
| View Audit Logs | ✓ | — |
| Change Database Path | ✓ | — |

---

## FAT Status Codes

| Status | Color |
|--------|-------|
| ✅ Approved | Green |
| ❌ Rejected | Red |
| ⏳ Pending | Orange |
| 💬 Approved with comments | Yellow |

---

## Project Structure

```
fat_system/
├── main.py
├── config/           settings, dynamic DB path config
├── database/         SQLAlchemy engine, WAL setup
├── models/           8 ORM models
├── repositories/     data access layer
├── services/         business logic (FAT, Auth, Attachments)
├── migrations/       Excel → SQLite import script
├── ui/
│   ├── login_window.py
│   ├── main_window.py
│   ├── dashboard/
│   ├── fat/          table, form, detail view
│   ├── projects/
│   ├── suppliers/
│   ├── consultants/
│   ├── attachments/  drag & drop panel, grid/list view
│   ├── reports/
│   └── settings/
├── assets/           logo.png, banner.png
├── installer/        setup.iss  (Inno Setup)
├── build.py
└── requirements.txt
```

---

## Logo

Place the company logo at:

```
assets/logo.png
```

Recommended: PNG with transparent background.  
The application loads it automatically — no code changes needed.

---

<div align="center">

**لا تنسونا من صالح الدعاء**

*Designed by Ahmed Hassanin*

</div>
