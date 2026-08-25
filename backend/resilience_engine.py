import pandas as pd
import numpy as np
import datetime
from typing import Dict, Any, Tuple, List

class DataResilienceEngine:
    """
    Cleans and normalizes messy data from Monday.com boards (Deals & Work Orders).
    Handles missing values, standardizes dates, sector names, financial amounts,
    and produces structured data quality warning logs.
    """

    SECTOR_MAPPING = {
        'mining': 'Mining',
        'powerline': 'Powerline',
        'power line': 'Powerline',
        'renewables': 'Renewables',
        'renewable': 'Renewables',
        'railways': 'Railways',
        'railway': 'Railways',
        'construction': 'Construction',
        'dsp': 'DSP',
        'tender': 'Tender',
        'oil & gas': 'Oil & Gas',
        'infrastructure': 'Infrastructure'
    }

    PROBABILITY_MAPPING = {
        'high': 0.80,
        'medium': 0.50,
        'low': 0.20,
        '100%': 1.00,
        '80%': 0.80,
        '50%': 0.50,
        '20%': 0.20,
        'won': 1.00,
        'dead': 0.00
    }

    @staticmethod
    def parse_flexible_date(val: Any) -> str:
        """Parses dates of varying formats into YYYY-MM-DD or None."""
        if pd.isna(val) or val == '' or str(val).strip().lower() in ['nan', 'nat', 'none', 'null']:
            return None
        if isinstance(val, (pd.Timestamp, datetime.datetime, datetime.date)):
            return val.strftime('%Y-%m-%d')
        
        val_str = str(val).strip()
        # Handle header leaks or weird values
        if val_str.startswith('Close Date') or val_str.startswith('Tentative'):
            return None
            
        try:
            parsed = pd.to_datetime(val_str, errors='coerce')
            if pd.notna(parsed):
                return parsed.strftime('%Y-%m-%d')
        except Exception:
            pass
        return None

    @classmethod
    def clean_deals_data(cls, raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans raw Deals data.
        Returns (cleaned_df, quality_audit)
        """
        df = raw_df.copy()
        audit = {
            'total_rows': len(df),
            'missing_deal_names': 0,
            'missing_deal_values': 0,
            'missing_sectors': 0,
            'missing_dates': 0,
            'quality_caveats': []
        }

        # Filter out header-repeat rows if present
        if 'Deal Name' in df.columns:
            df = df[df['Deal Name'] != 'Deal Name'].copy()

        # Clean Deal Name
        audit['missing_deal_names'] = int(df['Deal Name'].isna().sum())
        df['deal_name'] = df['Deal Name'].fillna('Unnamed Deal').astype(str).str.strip()

        # Clean Owner Code
        df['owner_code'] = df['Owner code'].fillna('UNASSIGNED').astype(str).str.strip()

        # Clean Client Code
        df['client_code'] = df['Client Code'].fillna('UNKNOWN_CLIENT').astype(str).str.strip()

        # Clean Deal Status
        df['deal_status'] = df['Deal Status'].fillna('Unknown').astype(str).str.strip()

        # Clean Deal Stage
        df['deal_stage'] = df['Deal Stage'].fillna('Uncategorized').astype(str).str.strip()

        # Clean Sector/Service
        audit['missing_sectors'] = int(df['Sector/service'].isna().sum())
        def norm_sector(s):
            if pd.isna(s):
                return 'Other/Unspecified'
            s_clean = str(s).strip().lower()
            return cls.SECTOR_MAPPING.get(s_clean, str(s).strip().title())
        df['sector'] = df['Sector/service'].apply(norm_sector)

        # Clean Product Deal
        df['product_deal'] = df['Product deal'].fillna('Unspecified Product').astype(str).str.strip()

        # Clean Masked Deal Value
        audit['missing_deal_values'] = int(df['Masked Deal value'].isna().sum())
        df['deal_value'] = pd.to_numeric(df['Masked Deal value'], errors='coerce').fillna(0.0)

        # Clean Closure Probability
        def parse_prob(val):
            if pd.isna(val):
                return 0.5 # default moderate assumption
            val_str = str(val).strip().lower()
            return cls.PROBABILITY_MAPPING.get(val_str, 0.5)
        df['closure_probability'] = df['Closure Probability'].apply(parse_prob)

        # Calculate Weighted Deal Value (Probability * Deal Value)
        df['weighted_deal_value'] = df['deal_value'] * df['closure_probability']

        # Clean Dates
        df['close_date'] = df['Close Date (A)'].apply(cls.parse_flexible_date)
        df['tentative_close_date'] = df['Tentative Close Date'].apply(cls.parse_flexible_date)
        df['created_date'] = df['Created Date'].apply(cls.parse_flexible_date)

        # Determine effective date (Close Date or Tentative Close Date or Created Date)
        df['effective_date'] = df['close_date'].combine_first(df['tentative_close_date']).combine_first(df['created_date'])

        # Audit Caveats
        if audit['missing_deal_values'] > 0:
            pct = round((audit['missing_deal_values'] / audit['total_rows']) * 100, 1)
            audit['quality_caveats'].append(f"⚠️ {audit['missing_deal_values']} deals ({pct}%) are missing numeric Deal Value. Defaulted to ₹0 for aggregates.")

        if audit['missing_sectors'] > 0:
            audit['quality_caveats'].append(f"⚠️ {audit['missing_sectors']} deals lack sector classification. Grouped under 'Other/Unspecified'.")

        return df, audit

    @classmethod
    def clean_work_orders_data(cls, raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cleans raw Work Orders data.
        Returns (cleaned_df, quality_audit)
        """
        df = raw_df.copy()
        
        # If headers are in row 0, elevate them
        if 'Unnamed: 0' in df.columns or df.columns[0] == 0:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

        audit = {
            'total_rows': len(df),
            'missing_amount': 0,
            'missing_billed_value': 0,
            'quality_caveats': []
        }

        # Filter out header-repeat rows if present
        if 'Deal name masked' in df.columns:
            df = df[df['Deal name masked'] != 'Deal name masked'].copy()

        # Deal name & Customer
        df['deal_name'] = df['Deal name masked'].fillna('Unnamed Work Order').astype(str).str.strip()
        df['customer_code'] = df['Customer Name Code'].fillna('UNKNOWN_COMPANY').astype(str).str.strip()
        df['serial_no'] = df['Serial #'].fillna('N/A').astype(str).str.strip()

        # Work classification
        df['nature_of_work'] = df['Nature of Work'].fillna('Unspecified').astype(str).str.strip()
        df['execution_status'] = df['Execution Status'].fillna('Unknown').astype(str).str.strip()
        df['owner_code'] = df['BD/KAM Personnel code'].fillna('UNASSIGNED').astype(str).str.strip()

        # Sector
        def norm_sector(s):
            if pd.isna(s):
                return 'Other/Unspecified'
            s_clean = str(s).strip().lower()
            return cls.SECTOR_MAPPING.get(s_clean, str(s).strip().title())
        df['sector'] = df['Sector'].apply(norm_sector)

        # Software Deliverable
        df['software_deliverable'] = df['Is any Skylark software platform part of the client deliverables in this deal?'].fillna('NONE').astype(str).str.strip().str.upper()

        # Amounts & Billing
        audit['missing_amount'] = int(df['Amount in Rupees (Excl of GST) (Masked)'].isna().sum())
        df['amount_excl_gst'] = pd.to_numeric(df['Amount in Rupees (Excl of GST) (Masked)'], errors='coerce').fillna(0.0)
        df['amount_incl_gst'] = pd.to_numeric(df['Amount in Rupees (Incl of GST) (Masked)'], errors='coerce').fillna(0.0)

        df['billed_excl_gst'] = pd.to_numeric(df['Billed Value in Rupees (Excl of GST.) (Masked)'], errors='coerce').fillna(0.0)
        df['billed_incl_gst'] = pd.to_numeric(df['Billed Value in Rupees (Incl of GST.) (Masked)'], errors='coerce').fillna(0.0)
        df['collected_incl_gst'] = pd.to_numeric(df['Collected Amount in Rupees (Incl of GST.) (Masked)'], errors='coerce').fillna(0.0)

        df['amount_to_be_billed_excl'] = pd.to_numeric(df['Amount to be billed in Rs. (Exl. of GST) (Masked)'], errors='coerce').fillna(0.0)
        df['amount_receivable'] = pd.to_numeric(df['Amount Receivable (Masked)'], errors='coerce').fillna(0.0)

        # Fix Billing Status typos ('BIlled' -> 'Billed')
        def norm_billing_status(val):
            if pd.isna(val):
                return 'Unknown'
            v = str(val).strip()
            if v.lower() in ['billed', 'billed']:
                return 'Billed'
            if v.lower() == 'partially billed':
                return 'Partially Billed'
            if v.lower() == 'not billed yet':
                return 'Not Billed Yet'
            if v.lower() == 'update required':
                return 'Update Required'
            return v
        df['billing_status'] = df['Billing Status'].apply(norm_billing_status)
        df['wo_status'] = df['WO Status (billed)'].fillna('Open').astype(str).str.strip()

        # Dates
        df['data_delivery_date'] = df['Data Delivery Date'].apply(cls.parse_flexible_date)
        df['po_date'] = df['Date of PO/LOI'].apply(cls.parse_flexible_date)
        df['start_date'] = df['Probable Start Date'].apply(cls.parse_flexible_date)
        df['end_date'] = df['Probable End Date'].apply(cls.parse_flexible_date)
        df['last_invoice_date'] = df['Last invoice date'].apply(cls.parse_flexible_date)

        # Audit Caveats
        unbilled_count = len(df[df['billed_excl_gst'] == 0])
        if unbilled_count > 0:
            audit['quality_caveats'].append(f"ℹ️ {unbilled_count} work orders have ₹0 billed value (either not billed yet or pending execution).")

        return df, audit

    @classmethod
    def load_and_clean_all(cls, deals_file: str, wo_file: str) -> Dict[str, Any]:
        """Loads both files and produces cleaned dataframes and quality audits."""
        deals_raw = pd.read_excel(deals_file, sheet_name="Deal tracker")
        wo_raw = pd.read_excel(wo_file, sheet_name="work order tracker")

        cleaned_deals, deals_audit = cls.clean_deals_data(deals_raw)
        cleaned_wo, wo_audit = cls.clean_work_orders_data(wo_raw)

        return {
            'deals': cleaned_deals,
            'work_orders': cleaned_wo,
            'deals_audit': deals_audit,
            'work_orders_audit': wo_audit
        }
