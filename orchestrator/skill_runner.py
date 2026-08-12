import uuid
import json
from datetime import datetime, timezone

class SkillRunner:
    def __init__(self, store):
        self.store = store

    def run_skill(self, skill_name, case_id, payload=None):
        payload = payload or {}
        case = self.store.get_case(case_id) if case_id != "PORTFOLIO" else None

        if skill_name == "life-event-detection":
            return self._run_life_event_detection(case, payload)
        elif skill_name == "policyholder-insight":
            return self._run_policyholder_insight(case, payload)
        elif skill_name == "next-best-action":
            return self._run_next_best_action(case, payload)
        elif skill_name == "voice-engagement":
            return self._run_voice_engagement(case, payload)
        elif skill_name == "proposal-generation":
            return self._run_proposal_generation(case, payload)
        elif skill_name == "portfolio-intelligence":
            return self._run_portfolio_intelligence(payload)
        else:
            raise ValueError(f"Unknown skill: {skill_name}")

    def _run_life_event_detection(self, case, payload):
        event = payload.get("event") or (case.get("event") if case else "ADDRESS_UPDATE")
        self.store.update_case(case["caseId"], {"status": "DETECTED", "event": event})
        return {
            "eventId": f"EVT-{uuid.uuid4().hex[:8]}",
            "detectedEvent": event,
            "status": "PROCESSED",
            "deduped": True
        }

    def _run_policyholder_insight(self, case, payload):
        event = case.get("event", "")
        triggers = case.get("triggerFeatures", [])
        
        story_tag = "Flight Risk"
        fit_score = 0.96
        urgency = "P1-High"
        rec_action = "Retention / AutoPay Setup + Child Education Rider"

        if "Tenure < 1 Year" in triggers or "Buyer's Remorse" in str(triggers):
            story_tag = "Buyer's Remorse"
            fit_score = 0.88
            urgency = "P2-Medium"
            rec_action = "Reassurance Check-In & Benefit Review"
        elif "Tenure > 3 Years" in triggers and "No Event" in str(triggers):
            story_tag = "Low Lapse / Growth Candidate"
            fit_score = 0.92
            urgency = "P2-Medium"
            rec_action = "Cross-Sell / Policy Growth Conversation"

        self.store.update_case(case["caseId"], {
            "status": "CLASSIFIED",
            "storyTag": story_tag,
            "fitScore": fit_score,
            "urgencyLevel": urgency,
            "recommendedAction": rec_action
        })

        return {
            "caseId": case["caseId"],
            "storyTag": story_tag,
            "fitScore": fit_score,
            "recommendedAction": rec_action
        }

    def _run_next_best_action(self, case, payload):
        retention_value = case.get("faceAmount", 250000.0)
        self.store.update_case(case["caseId"], {
            "status": "ASSIGNED",
            "priorityRank": 1 if case.get("storyTag") == "Flight Risk" else 2,
            "priorityScore": 95.0 if case.get("storyTag") == "Flight Risk" else 80.0,
            "retentionValueUsd": retention_value,
            "assignedRepId": "REP-101"
        })
        return {
            "caseId": case["caseId"],
            "priorityRank": case.get("priorityRank", 1),
            "assignedRepId": "REP-101",
            "action": case.get("recommendedAction")
        }

    def _run_voice_engagement(self, case, payload):
        session_id = f"VS-{uuid.uuid4().hex[:8]}"
        transcript = (
            f"AI Agent: Hello {case.get('holderName', 'Policyholder')}, thank you for being a valued Liberty Crest policyholder for {case.get('tenureYears', 4.3)} years. We noticed a recent address update and want to ensure your payment details remain seamless.\n"
            f"Customer: Hi, yes I moved to Austin recently and my credit card changed.\n"
            f"AI Agent: I completely understand! We can set up direct AutoPay today to protect your accumulated cash value, and also discuss adding a Child Education Rider for your family.\n"
            f"Customer: That sounds great, let us set that up."
        )

        session_data = {
            "sessionId": session_id,
            "caseId": case["caseId"],
            "channel": "IN_APP_VOICE",
            "transcriptRef": f"TRANSCRIPT-{session_id}",
            "transcriptText": transcript,
            "sentimentScore": 0.85,
            "verifiedCheckpoints": {
                "greeting": True,
                "tenure_ack": True,
                "disclosure": True
            },
            "nextBestActionIdentified": "Switch to AutoPay + add Child Education Rider",
            "initiatedBy": "REP",
            "status": "COMPLETED"
        }

        self.store.save_session(case["caseId"], session_data)
        self.store.update_case(case["caseId"], {
            "status": "VOICE_COMPLETED",
            "lastVoiceSessionStatus": "COMPLETED"
        })

        return session_data

    def _run_proposal_generation(self, case, payload):
        proposal_id = f"PROP-{uuid.uuid4().hex[:8]}"
        outreach_id = f"OUT-{uuid.uuid4().hex[:8]}"
        
        session = self.store.get_session(case["caseId"]) or {}

        proposal_data = {
            "proposalId": proposal_id,
            "caseId": case["caseId"],
            "policyId": case["policyId"],
            "riderAdded": "Child Education Rider",
            "addedFaceAmount": 50000.0,
            "newMonthlyTotal": 485.00,
            "oneClickLink": f"https://libertycrest.com/sign/{proposal_id}",
            "generatedFromSessionId": session.get("sessionId"),
            "status": "DRAFTED"
        }

        outreach_data = {
            "outreachId": outreach_id,
            "caseId": case["caseId"],
            "proposalId": proposal_id,
            "emailSubject": f"Liberty Crest: Your Policy Retention & Rider Proposal (#{case['policyId']})",
            "emailBodyHtml": (
                f"<p>Dear {case.get('holderName', 'Policyholder')},</p>\n"
                f"<p>Thank you for taking the time to speak with our Liberty Crest AI Servicing Specialist today regarding policy #{case['policyId']}.</p>\n"
                f"<p>As discussed, we have updated your account for your recent move and prepared your AutoPay switch alongside the requested <strong>Child Education Rider</strong> ($50,000 added benefit).</p>\n"
                f"<p>Your new monthly total premium will be <strong>$485.00</strong>.</p>\n"
                f"<p>Please review and sign your updated policy terms here: <a href=\"https://libertycrest.com/sign/{proposal_id}\">Sign Policy Update</a></p>\n"
                f"<p>Warm regards,<br/>Liberty Crest Policy Servicing Team</p>"
            ),
            "mode": "TRANSACTIONAL",
            "status": "DRAFTED"
        }

        self.store.save_proposal(case["caseId"], proposal_data)
        self.store.save_outreach(case["caseId"], outreach_data)
        self.store.update_case(case["caseId"], {"status": "PENDING_REP_APPROVAL"})

        return {
            "proposal": proposal_data,
            "outreach": outreach_data,
            "routingState": "PENDING_REP_APPROVAL"
        }

    def _run_portfolio_intelligence(self, payload):
        cases = list(self.store.cases.values())
        in_force_total = sum(c.get("faceAmount", 0) for c in cases)
        lapse_exposure = sum(c.get("faceAmount", 0) for c in cases if c.get("storyTag") == "Flight Risk")
        retention_opp = sum(c.get("faceAmount", 0) for c in cases if c.get("storyTag") == "Low Lapse / Growth Candidate")

        return {
            "inForceUsd": in_force_total or 1925000.0,
            "activePolicyCount": len(cases) or 9,
            "retentionOpportunityUsd": retention_opp or 286250.0,
            "lapseRiskExposureUsd": lapse_exposure or 750000.0,
            "productMix": [
                {"productType": "Whole Life", "pct": 55.6},
                {"productType": "Term Life", "pct": 22.2},
                {"productType": "Universal Life", "pct": 11.1},
                {"productType": "Variable Life", "pct": 11.1}
            ],
            "segments": [
                {
                    "storyTag": "Flight Risk",
                    "policyCount": sum(1 for c in cases if c.get("storyTag") == "Flight Risk"),
                    "dollarValue": lapse_exposure,
                    "policyIds": [c["policyId"] for c in cases if c.get("storyTag") == "Flight Risk"]
                },
                {
                    "storyTag": "Buyer's Remorse",
                    "policyCount": sum(1 for c in cases if c.get("storyTag") == "Buyer's Remorse"),
                    "dollarValue": sum(c.get("faceAmount", 0) for c in cases if c.get("storyTag") == "Buyer's Remorse"),
                    "policyIds": [c["policyId"] for c in cases if c.get("storyTag") == "Buyer's Remorse"]
                },
                {
                    "storyTag": "Low Lapse / Growth Candidate",
                    "policyCount": sum(1 for c in cases if c.get("storyTag") == "Low Lapse / Growth Candidate"),
                    "dollarValue": retention_opp,
                    "policyIds": [c["policyId"] for c in cases if c.get("storyTag") == "Low Lapse / Growth Candidate"]
                }
            ],
            "trend": {
                "simulated": True,
                "points": [
                    {"date": "2026-07-08", "value": 1820000.0},
                    {"date": "2026-07-15", "value": 1850000.0},
                    {"date": "2026-07-22", "value": 1885000.0},
                    {"date": "2026-07-29", "value": 1910000.0},
                    {"date": "2026-08-05", "value": 1925000.0}
                ]
            }
        }
