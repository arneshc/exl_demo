import uuid
from datetime import datetime, timezone

def create_audit_entry(case_id, agent_name, reasoning_summary, input_refs=None, output_ref=None, **kwargs):
    if not case_id:
        case_id = kwargs.get("caseId")
    if not agent_name:
        agent_name = kwargs.get("agentName")
    if not reasoning_summary:
        reasoning_summary = kwargs.get("reasoningSummary")
    if not input_refs:
        input_refs = kwargs.get("inputRefs", {})
    if not output_ref:
        output_ref = kwargs.get("outputRef", {})

    return {
        "entryId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caseId": case_id,
        "agentName": agent_name,
        "reasoningSummary": reasoning_summary,
        "inputRefs": input_refs or {},
        "outputRef": output_ref or {}
    }
