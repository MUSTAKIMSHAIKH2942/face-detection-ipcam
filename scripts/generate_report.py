# scripts/generate_report.py

import sqlite3
import pandas as pd
import subprocess   
import os
from datetime import datetime

DB_FILE = "eyeq_alerts.db"
EXPORT_FOLDER = "reports"

def fetch_alerts(start_date=None, end_date=None):
    query = "SELECT * FROM alerts"
    params = []

    if start_date and end_date:
        query += " WHERE timestamp BETWEEN ? AND ?"
        params = [start_date, end_date]

    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(query, conn, params=params)

    return df

def export_to_csv(df, filename=None):
    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alerts_export_{timestamp}.csv"

    filepath = os.path.join(EXPORT_FOLDER, filename)
    df.to_csv(filepath, index=False)
    print(f"[EXPORT] CSV saved → {filepath}")

def export_to_pdf(df, filename=None):
    from fpdf import FPDF

    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alerts_export_{timestamp}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=9)

    col_width = pdf.w / (len(df.columns) + 1)
    row_height = 6

    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, txt=str(col), border=1)
    pdf.ln(row_height)

    # Rows
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, txt=str(item), border=1)
        pdf.ln(row_height)

    filepath = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(filepath)
    print(f"[EXPORT] PDF saved → {filepath}")

if __name__ == "__main__":
    print("Generating alert report from alerts database...")

    # You may later take input from UI or CLI args for custom dates
    df = fetch_alerts()
    if not df.empty:
        export_to_csv(df)
        export_to_pdf(df)
    else:
        print("[INFO] No alerts found in database.")
