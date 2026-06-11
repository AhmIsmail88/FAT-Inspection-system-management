"""
migrate_from_excel.py
─────────────────────
Converts the existing Excel FAT tracking file into the SQLite database.

Usage:
    python migrations/migrate_from_excel.py --excel path/to/FAT_INSPECTION.xlsx

What it does:
  1. Extracts unique Projects, Suppliers, Consultants from all sheets
  2. Builds per-project Supplier Contacts and Consultant Contacts
  3. Creates all FAT Records with proper foreign keys
  4. Creates default Admin user
  5. Reports summary at the end
"""

import argparse
import sys
import os
from datetime import datetime, date
from pathlib import Path

# ── Make sure we can import from the project root ────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy.orm import Session

from database.connection import engine, init_db
from models import (
    Project, Supplier, SupplierContact,
    Consultant, ConsultantContact,
    FATRecord, User,
)
from config.settings import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


# ─── Helpers ─────────────────────────────────────────────────────────────────

def clean(val) -> str | None:
    """Convert any Excel cell value to a clean string or None."""
    if val is None:
        return None
    s = str(val).strip()
    if s.lower() in ("n.a", "n.a.", "na", "none", "nan", "", "-"):
        return None
    return s


def parse_excel_date(val) -> date | None:
    """Excel dates come as serial numbers (float) or already parsed."""
    if val is None or str(val).strip() in ("", "nan", "None"):
        return None
    if isinstance(val, (int, float)):
        try:
            from openpyxl.utils.datetime import from_excel
            return from_excel(int(val))
        except Exception:
            return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    try:
        return pd.to_datetime(str(val)).date()
    except Exception:
        return None


def normalize_status(val: str | None) -> str:
    """Map Excel status text to canonical DB status."""
    if not val:
        return "Pending"
    v = val.strip().lower()
    if "approved" in v and "comment" in v:
        return "Approved with comments"
    if "approved" in v:
        return "Approved"
    if "rejected" in v:
        return "Rejected"
    return "Pending"


# ─── Main Migration ──────────────────────────────────────────────────────────

class ExcelMigrator:
    def __init__(self, excel_path: str, session: Session):
        self.excel_path = excel_path
        self.session    = session
        self.s          = session   # shorthand

        # Lookup caches: name → DB id
        self.projects:   dict[str, int] = {}
        self.suppliers:  dict[str, int] = {}
        self.consultants: dict[str, int] = {}
        # (supplier_id, project_id, contact_name) → SupplierContact.id
        self.sup_contacts: dict[tuple, int] = {}
        # (consultant_id, project_id, contact_name) → ConsultantContact.id
        self.con_contacts: dict[tuple, int] = {}

    # ── Step 1: Read all sheets ──────────────────────────────────────────────
    def load_sheets(self) -> list[pd.DataFrame]:
        xl = pd.ExcelFile(self.excel_path)
        frames = []
        for sheet in xl.sheet_names:
            df = pd.read_excel(self.excel_path, sheet_name=sheet, header=None)
            # Find the header row (row with "Serial" or "serial")
            header_row = None
            for i, row in df.iterrows():
                row_vals = [str(v).strip().lower() for v in row.values]
                if "serial" in row_vals:
                    header_row = i
                    break
            if header_row is None:
                print(f"  [!] Sheet '{sheet}': no header row found, skipping.")
                continue
            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)
            df = df.dropna(how="all")
            # Normalize column names
            df.columns = [str(c).strip() for c in df.columns]
            df["_sheet"] = sheet
            frames.append(df)
            print(f"  [OK] Sheet '{sheet}': {len(df)} rows loaded")
        return frames

    # ── Step 2: Get or create lookup entities ────────────────────────────────
    def get_or_create_project(self, name: str) -> int:
        name = name.strip()
        if name in self.projects:
            return self.projects[name]
        obj = self.s.query(Project).filter_by(project_name=name).first()
        if not obj:
            obj = Project(project_name=name, status="Active")
            self.s.add(obj)
            self.s.flush()
        self.projects[name] = obj.id
        return obj.id

    def get_or_create_supplier(self, name: str) -> int:
        name = name.strip()
        if name in self.suppliers:
            return self.suppliers[name]
        obj = self.s.query(Supplier).filter_by(supplier_name=name).first()
        if not obj:
            obj = Supplier(supplier_name=name)
            self.s.add(obj)
            self.s.flush()
        self.suppliers[name] = obj.id
        return obj.id

    def get_or_create_consultant(self, name: str) -> int:
        name = name.strip()
        if name in self.consultants:
            return self.consultants[name]
        obj = self.s.query(Consultant).filter_by(company_name=name).first()
        if not obj:
            obj = Consultant(company_name=name)
            self.s.add(obj)
            self.s.flush()
        self.consultants[name] = obj.id
        return obj.id

    def get_or_create_supplier_contact(
        self, supplier_id: int, project_id: int,
        name: str, mobile: str | None, location_url: str | None
    ) -> int:
        key = (supplier_id, project_id, name)
        if key in self.sup_contacts:
            return self.sup_contacts[key]
        obj = (
            self.s.query(SupplierContact)
            .filter_by(supplier_id=supplier_id, project_id=project_id, name=name)
            .first()
        )
        if not obj:
            obj = SupplierContact(
                supplier_id=supplier_id,
                project_id=project_id,
                name=name,
                mobile=mobile,
                whatsapp=mobile,
            )
            # Store location URL on the supplier (if not set)
            if location_url:
                supplier = self.s.get(Supplier, supplier_id)
                if supplier and not supplier.location_url:
                    supplier.location_url = location_url
            self.s.add(obj)
            self.s.flush()
        self.sup_contacts[key] = obj.id
        return obj.id

    def get_or_create_consultant_contact(
        self, consultant_id: int, project_id: int,
        name: str, mobile: str | None, email: str | None
    ) -> int:
        key = (consultant_id, project_id, name)
        if key in self.con_contacts:
            return self.con_contacts[key]
        obj = (
            self.s.query(ConsultantContact)
            .filter_by(consultant_id=consultant_id, project_id=project_id, name=name)
            .first()
        )
        if not obj:
            obj = ConsultantContact(
                consultant_id=consultant_id,
                project_id=project_id,
                name=name,
                mobile=mobile,
                email=email,
            )
            self.s.add(obj)
            self.s.flush()
        self.con_contacts[key] = obj.id
        return obj.id

    # ── Step 3: Map a row to a FATRecord ────────────────────────────────────
    def _col(self, row, *candidates):
        """Return first matching column value from candidates (case-insensitive)."""
        for col in candidates:
            for actual_col in row.index:
                if str(actual_col).strip().lower() == col.lower():
                    v = row[actual_col]
                    if pd.notna(v):
                        return clean(str(v))
        return None

    def process_row(self, row, serial_counter: int) -> FATRecord | None:
        project_name    = self._col(row, "Project")
        supplier_name   = self._col(row, "Factory & Supplier", "Supplier")
        description     = self._col(row, "Desc.", "Description", " Desc. ")
        quantity        = self._col(row, "Quantity")
        status_raw      = self._col(row, "Status")
        reference_no    = self._col(row, "Reference")
        sap_no          = self._col(row, "po/sap", "SAP")
        po_no           = self._col(row, "PO no", "PO No")
        major_comments  = self._col(row, "Major Comments")
        date_raw        = self._col(row, "Date")
        supplier_person = self._col(row, "Supplier Person")
        contact_mob     = self._col(row, "Contact Mob")
        location_url    = self._col(row, "Location")
        consultant_name = self._col(row, "Consultant")
        con_contact_name= self._col(row, "Name")
        con_contact_mob = self._col(row, "Mob")
        con_contact_email = self._col(row, "Email")

        if not project_name or not supplier_name:
            return None

        project_id  = self.get_or_create_project(project_name)
        supplier_id = self.get_or_create_supplier(supplier_name)

        # Supplier contact (responsible engineer per project)
        supplier_contact_id = None
        if supplier_person:
            supplier_contact_id = self.get_or_create_supplier_contact(
                supplier_id, project_id, supplier_person, contact_mob, location_url
            )

        # Consultant + consultant contact
        consultant_id         = None
        consultant_contact_id = None
        if consultant_name:
            consultant_id = self.get_or_create_consultant(consultant_name)
            if con_contact_name and con_contact_name not in ("N.A", "N.A."):
                consultant_contact_id = self.get_or_create_consultant_contact(
                    consultant_id, project_id,
                    con_contact_name, con_contact_mob, con_contact_email
                )

        # Inspection date
        try:
            insp_date = parse_excel_date(row.get("Date") or row.get(" Date "))
        except Exception:
            insp_date = None

        record = FATRecord(
            serial_no             = serial_counter,
            project_id            = project_id,
            supplier_id           = supplier_id,
            supplier_contact_id   = supplier_contact_id,
            consultant_id         = consultant_id,
            consultant_contact_id = consultant_contact_id,
            inspection_type       = "FAT",
            inspection_date       = insp_date,
            description           = description,
            quantity              = quantity,
            status                = normalize_status(status_raw),
            reference_no          = reference_no,
            sap_no                = sap_no,
            po_no                 = po_no,
            major_comments        = major_comments,
        )
        return record

    # ── Step 4: Create default admin ────────────────────────────────────────
    def create_default_admin(self):
        existing = self.s.query(User).filter_by(username=DEFAULT_ADMIN_USERNAME).first()
        if not existing:
            admin = User(
                username      = DEFAULT_ADMIN_USERNAME,
                password_hash = User.hash_password(DEFAULT_ADMIN_PASSWORD),
                full_name     = "System Administrator",
                role          = "Admin",
                is_active     = True,
            )
            self.s.add(admin)
            self.s.flush()
            print(f"  [OK] Default admin created: {DEFAULT_ADMIN_USERNAME} / {DEFAULT_ADMIN_PASSWORD}")

    # ── Run ──────────────────────────────────────────────────────────────────
    def run(self):
        print(f"\n{'='*60}")
        print("  HAC FAT System — Excel Migration")
        print(f"{'='*60}")
        print(f"\n-> Reading: {self.excel_path}\n")

        init_db()

        frames = self.load_sheets()
        if not frames:
            print("No data found. Aborting.")
            return

        total_records   = 0
        skipped_rows    = 0
        serial_counter  = 1

        for df in frames:
            sheet_name = df["_sheet"].iloc[0] if "_sheet" in df.columns else "?"
            print(f"\n-> Processing sheet: {sheet_name}")

            for _, row in df.iterrows():
                try:
                    record = self.process_row(row, serial_counter)
                    if record:
                        self.s.add(record)
                        serial_counter  += 1
                        total_records   += 1
                    else:
                        skipped_rows += 1
                except Exception as e:
                    print(f"  [!] Row error: {e}")
                    skipped_rows += 1

        self.create_default_admin()
        self.s.commit()

        print(f"\n{'='*60}")
        print("  Migration Complete!")
        print(f"{'='*60}")
        print(f"  Projects:    {len(self.projects)}")
        print(f"  Suppliers:   {len(self.suppliers)}")
        print(f"  Consultants: {len(self.consultants)}")
        print(f"  FAT Records: {total_records}")
        print(f"  Skipped:     {skipped_rows}")
        print(f"  DB Path:     {Path(self.s.bind.url.database).resolve()}")
        print(f"{'='*60}\n")


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Excel FAT data to SQLite")
    parser.add_argument(
        "--excel",
        required=True,
        help="Path to the Excel file (e.g. FAT___INSPECTION.xlsx)"
    )
    args = parser.parse_args()

    if not Path(args.excel).exists():
        print(f"Error: File not found: {args.excel}")
        sys.exit(1)

    from database.connection import SessionLocal
    session = SessionLocal()

    try:
        migrator = ExcelMigrator(args.excel, session)
        migrator.run()
    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        session.close()
