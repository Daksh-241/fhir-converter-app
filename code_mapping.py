import os
from typing import Dict, Optional
import pandas as pd


class CodeMappingService:
    """
    Loads and serves code mappings for ICD-11 and AYUSH traditions (Ayurveda, Siddha, Unani).

    Expected dataset columns (case-insensitive, tolerant to spaces/underscores):
      - disease / condition / condition_name
      - icd11 / icd_11 / icd11_code
      - ayurveda / ayurveda_code
      - siddha / siddha_code
      - unani / unani_code
      - snomed / snomed_code (optional)
      - loinc / loinc_code (optional)

    Sources (first found is used):
      1) "mapping 4.xlsx" (existing in repo)
      2) code_mappings.xlsx
      3) code_mappings.csv
    """

    DEFAULT_SYSTEMS = {
        "icd11": "http://id.who.int/icd/release/11/mms",
        "snomed": "http://snomed.info/sct",
        "loinc": "http://loinc.org",
        # Provisional AYUSH CodeSystem URIs (replace with official NRCeS URIs if available)
        "ayurveda": "https://nrces.in/terminology/CodeSystem/ayush-ayurveda",
        "siddha": "https://nrces.in/terminology/CodeSystem/ayush-siddha",
        "unani": "https://nrces.in/terminology/CodeSystem/ayush-unani",
    }

    def __init__(self, custom_systems: Optional[Dict[str, str]] = None):
        self.systems = {**self.DEFAULT_SYSTEMS, **(custom_systems or {})}
        self.df = self._load_dataset()

    def _normalize_col(self, name: str) -> str:
        return name.strip().lower().replace(" ", "_")

    def _load_dataset(self) -> Optional[pd.DataFrame]:
        candidates = [
            "mapping 4.xlsx",
            "code_mappings.xlsx",
            "code_mappings.csv",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    if path.endswith(".csv"):
                        df = pd.read_csv(path)
                    else:
                        df = pd.read_excel(path)
                    # Normalize columns
                    df = df.rename(columns={c: self._normalize_col(c) for c in df.columns})
                    return df
                except Exception:
                    continue
        return None

    def _col(self, *aliases: str) -> Optional[str]:
        if self.df is None:
            return None
        cols = set(self.df.columns)
        for a in aliases:
            n = self._normalize_col(a)
            if n in cols:
                return n
        return None

    def find_by_disease(self, disease_name: str) -> Optional[Dict[str, str]]:
        if self.df is None or not disease_name:
            return None

        disease_col = self._col("disease", "condition", "condition_name")
        if disease_col is None:
            return None

        # Case-insensitive exact match first
        mask = self.df[disease_col].astype(str).str.strip().str.lower() == disease_name.strip().lower()
        match_df = self.df[mask]
        if match_df.empty:
            # Fallback: contains
            mask = self.df[disease_col].astype(str).str.lower().str.contains(disease_name.strip().lower())
            match_df = self.df[mask]
            if match_df.empty:
                return None

        row = match_df.iloc[0]

        def get_val(*aliases: str) -> Optional[str]:
            c = self._col(*aliases)
            if c and pd.notna(row.get(c)):
                v = str(row.get(c)).strip()
                return v or None
            return None

        return {
            "disease": str(row.get(disease_col, "")).strip(),
            "icd11_code": get_val("icd11", "icd_11", "icd11_code"),
            "ayurveda_code": get_val("ayurveda", "ayurveda_code"),
            "siddha_code": get_val("siddha", "siddha_code"),
            "unani_code": get_val("unani", "unani_code"),
            "snomed_code": get_val("snomed", "snomed_code"),
            "loinc_code": get_val("loinc", "loinc_code"),
        }

    def find_by_any(self,
                     disease: Optional[str] = None,
                     snomed: Optional[str] = None,
                     icd11: Optional[str] = None,
                     ayurveda: Optional[str] = None,
                     siddha: Optional[str] = None,
                     unani: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Resolve mapping by any provided key; prioritizes exact matches, then contains for disease.
        """
        if self.df is None:
            return None

        # Build candidate masks
        masks = []

        def eq_mask(col_aliases, value):
            c = self._col(*col_aliases)
            if not c or value is None or str(value).strip() == "":
                return None
            val = str(value).strip().lower()
            return self.df[c].astype(str).str.strip().str.lower() == val

        # Exact matches by code first
        for aliases, value in [
            (("snomed", "snomed_code"), snomed),
            (("icd11", "icd_11", "icd11_code"), icd11),
            (("ayurveda", "ayurveda_code"), ayurveda),
            (("siddha", "siddha_code"), siddha),
            (("unani", "unani_code"), unani),
        ]:
            m = eq_mask(aliases, value)
            if m is not None:
                masks.append(m)

        # Disease exact then contains
        if disease:
            disease_col = self._col("disease", "condition", "condition_name")
            if disease_col:
                val = str(disease).strip().lower()
                masks.append(self.df[disease_col].astype(str).str.strip().str.lower() == val)

        # Combine masks with OR
        if not masks:
            return None
        combined = masks[0]
        for m in masks[1:]:
            combined = combined | m

        match_df = self.df[combined]
        if match_df.empty and disease:
            # fallback contains disease
            disease_col = self._col("disease", "condition", "condition_name")
            if disease_col:
                contains_mask = self.df[disease_col].astype(str).str.lower().str.contains(str(disease).strip().lower())
                match_df = self.df[contains_mask]

        if match_df.empty:
            return None

        row = match_df.iloc[0]

        def get_val(*aliases: str) -> Optional[str]:
            c = self._col(*aliases)
            if c and pd.notna(row.get(c)):
                v = str(row.get(c)).strip()
                return v or None
            return None

        disease_col = self._col("disease", "condition", "condition_name")
        return {
            "disease": str(row.get(disease_col, "")).strip() if disease_col else None,
            "icd11_code": get_val("icd11", "icd_11", "icd11_code"),
            "ayurveda_code": get_val("ayurveda", "ayurveda_code"),
            "siddha_code": get_val("siddha", "siddha_code"),
            "unani_code": get_val("unani", "unani_code"),
            "snomed_code": get_val("snomed", "snomed_code"),
            "loinc_code": get_val("loinc", "loinc_code"),
        }

    def systems_for_response(self) -> Dict[str, str]:
        return dict(self.systems)


