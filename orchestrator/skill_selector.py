import os
import json
from google import genai
from google.genai import types

class SkillSelector:
    def __init__(self, skills_loader):
        self.skills_loader = skills_loader
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def select_skill(self, case, payload=None):
        skills_prompt = self.skills_loader.format_skills_for_prompt()
        case_status = case.get("status") if case else "UNKNOWN"
        case_id = case.get("caseId") if case else "NONE"
        has_story = bool(case.get("storyTag")) if case else False
        has_rec = bool(case.get("recommendedAction")) if case else False
        last_voice_status = case.get("lastVoiceSessionStatus") if case else None

        # Rule-based fast routing fallback
        if case_status == "DETECTED" and not has_story:
            return "policyholder-insight", "Case is in DETECTED state without a story tag. Needs archetype classification."
        elif case_status == "CLASSIFIED" or (has_story and not case.get("priorityRank")):
            return "next-best-action", "Case is CLASSIFIED. Needs queue priority ranking."
        elif case_status == "ENGAGEMENT_INITIATED":
            return "voice-engagement", "Case has ENGAGEMENT_INITIATED status. Requires voice engagement session."
        elif case_status == "VOICE_COMPLETED" or last_voice_status == "COMPLETED":
            return "proposal-generation", "Voice engagement completed. Assembling proposal and outreach draft."

        if not self.client:
            return "policyholder-insight", "Default fallback skill selected."

        prompt = f"""You are the Root Orchestrator for Liberty Crest Policyholder Retention System.
Available Skills and Frontmatter Descriptions:
{skills_prompt}

Current Case State:
- Case ID: {case_id}
- Status: {case_status}
- Story Tag: {case.get('storyTag')}
- Priority Rank: {case.get('priorityRank')}
- Recommended Action: {case.get('recommendedAction')}

Evaluate the Case state against the skill descriptions and select the single best matching skill name.
Return JSON format:
{{
  "selectedSkill": "skill-name",
  "reasoning": "Clear justification matching the skill frontmatter"
}}
"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            res = json.loads(response.text)
            return res.get("selectedSkill"), res.get("reasoning")
        except Exception as e:
            print(f"Gemini Skill Selector Error: {e}")
            return "policyholder-insight", "Fallback error selection."
