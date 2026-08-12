import os
import yaml
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / ".agent" / "skills"

class SkillMetadata:
    def __init__(self, name, description, path, frontmatter=None, content=""):
        self.name = name
        self.description = description
        self.path = path
        self.frontmatter = frontmatter or {}
        self.content = content

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "path": str(self.path),
            "frontmatter": self.frontmatter,
            "content": self.content
        }

class SkillsLoader:
    def __init__(self, skills_dir=SKILLS_DIR):
        self.skills_dir = Path(skills_dir)
        self.skills = {}
        self.reload_skills()

    def reload_skills(self):
        self.skills = {}
        if not self.skills_dir.exists():
            return

        for skill_folder in self.skills_dir.iterdir():
            if skill_folder.is_dir():
                skill_file = skill_folder / "SKILL.md"
                if skill_file.exists():
                    skill_meta = self._parse_skill_file(skill_folder.name, skill_file)
                    if skill_meta:
                        self.skills[skill_meta.name] = skill_meta

    def _parse_skill_file(self, folder_name, file_path):
        try:
            text = file_path.read_text(encoding="utf-8")
            if text.startswith("---"):
                parts = text.split("---", 2)
                if len(parts) >= 3:
                    yaml_str = parts[1]
                    content = parts[2].strip()
                    frontmatter = yaml.safe_load(yaml_str) or {}
                    name = frontmatter.get("name", folder_name)
                    description = frontmatter.get("description", "")
                    return SkillMetadata(
                        name=name,
                        description=description,
                        path=file_path,
                        frontmatter=frontmatter,
                        content=content
                    )
            return SkillMetadata(
                name=folder_name,
                description="",
                path=file_path,
                frontmatter={},
                content=text
            )
        except Exception as e:
            print(f"Error parsing skill file {file_path}: {e}")
            return None

    def get_skill(self, name):
        return self.skills.get(name)

    def get_all_skills(self, include_archetypes=False):
        if include_archetypes:
            return list(self.skills.values())
        return [s for name, s in self.skills.items() if name != "ui-dashboard-conventions"]

    def format_skills_for_prompt(self):
        skills_formatted = []
        for name, skill in self.skills.items():
            if name == "ui-dashboard-conventions":
                continue
            skills_formatted.append(f"Skill: {name}\nDescription: {skill.description}\n")
        return "\n".join(skills_formatted)
