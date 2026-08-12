import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

class DataStore:
    def __init__(self, data_dir=DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.cases = {}
        self.sessions = {}
        self.proposals = {}
        self.outreach = {}
        self.audit_entries = []

        self._load_initial_dataset()

    def _load_initial_dataset(self):
        xml_file = self.data_dir / "sample_customer_dataset.xml"
        if not xml_file.exists():
            return

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for record in root.findall("CustomerRecord"):
                p = record.find("Policy")
                h = record.find("Policyholder")
                c = record.find("CaseContext")
                
                case_id = f"CASE-{p.findtext('policy_id')}"
                case_data = {
                    "caseId": case_id,
                    "policyId": p.findtext("policy_id"),
                    "holderId": h.findtext("holder_id"),
                    "holderName": h.findtext("name"),
                    "dependentsCount": int(h.findtext("dependents_count", "0")),
                    "monthlyPremium": float(p.findtext("monthly_premium", "0")),
                    "faceAmount": float(p.findtext("face_amount", "0")),
                    "cashValue": float(p.findtext("cash_value", "0")),
                    "tenureYears": float(p.findtext("tenure_years", "0")),
                    "location": h.findtext("location"),
                    "status": "DETECTED",
                    "event": c.findtext("event") if c is not None else None,
                    "triggerFeatures": json.loads(c.findtext("trigger_features", "[]")) if c is not None and c.findtext("trigger_features") else [],
                    "storyTag": None,
                    "fitScore": None,
                    "urgencyLevel": None,
                    "priorityScore": None,
                    "priorityRank": None,
                    "assignedRepId": None,
                    "recommendedAction": None,
                    "createdAt": datetime.now(timezone.utc).isoformat(),
                    "updatedAt": datetime.now(timezone.utc).isoformat()
                }
                self.cases[case_id] = case_data
        except Exception as e:
            print(f"Error parsing XML dataset: {e}")

    def get_case(self, case_id):
        return self.cases.get(case_id)

    def update_case(self, case_id, updates):
        if case_id in self.cases:
            self.cases[case_id].update(updates)
            self.cases[case_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            return self.cases[case_id]
        return None

    def save_session(self, case_id, session_data):
        self.sessions[case_id] = session_data
        return session_data

    def get_session(self, case_id):
        return self.sessions.get(case_id)

    def save_proposal(self, case_id, proposal_data):
        self.proposals[case_id] = proposal_data
        return proposal_data

    def get_proposal(self, case_id):
        return self.proposals.get(case_id)

    def save_outreach(self, case_id, outreach_data):
        self.outreach[case_id] = outreach_data
        return outreach_data

    def get_outreach(self, case_id):
        return self.outreach.get(case_id)

    def append_audit_entry(self, entry):
        self.audit_entries.append(entry)

    def get_audit_log(self, case_id=None):
        if case_id:
            return [e for e in self.audit_entries if e.get("caseId") == case_id]
        return self.audit_entries
