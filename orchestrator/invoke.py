from orchestrator.skills_loader import SkillsLoader
from orchestrator.store import DataStore
from orchestrator.skill_selector import SkillSelector
from orchestrator.skill_runner import SkillRunner
from orchestrator.audit import create_audit_entry

_skills_loader = SkillsLoader()
_store = DataStore()
_skill_selector = SkillSelector(_skills_loader)
_skill_runner = SkillRunner(_store)

def invoke_agent(request_data):
    case_id = request_data.get("caseId")
    explicit_skill = request_data.get("skill")
    payload = request_data.get("payload", {})

    case = _store.get_case(case_id) if case_id and case_id != "PORTFOLIO" else None

    if explicit_skill:
        selected_skill = explicit_skill
        reasoning = f"Explicitly invoked skill: {explicit_skill}"
    else:
        selected_skill, reasoning = _skill_selector.select_skill(case, payload)

    try:
        output = _skill_runner.run_skill(selected_skill, case_id, payload)
        
        audit_entry = create_audit_entry(
            case_id=case_id,
            agent_name=selected_skill,
            reasoning_summary=reasoning,
            input_refs={"caseId": case_id, "payload": payload},
            output_ref=output
        )
        _store.append_audit_entry(audit_entry)

        return {
            "status": "SUCCESS",
            "executedSkill": selected_skill,
            "caseId": case_id,
            "output": output,
            "auditEntry": audit_entry
        }
    except Exception as e:
        error_entry = create_audit_entry(
            case_id=case_id,
            agent_name=selected_skill or "unknown",
            reasoning_summary=f"Execution error: {str(e)}",
            input_refs={"caseId": case_id, "payload": payload},
            output_ref={"error": str(e)}
        )
        _store.append_audit_entry(error_entry)
        return {
            "status": "ERROR",
            "error": str(e),
            "auditEntry": error_entry
        }
