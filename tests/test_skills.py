from pathlib import Path

from polymath_agent.skills import SkillsRepository


def test_discovers_valid_skill_and_loads_optional_file(tmp_path: Path) -> None:
    skill_dir = tmp_path / "demo-skill"
    references = skill_dir / "references"
    references.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: demo-skill\n"
        "description: Demonstrate skill loading for tests.\n"
        "---\n\n"
        "# Demo Skill\n",
        encoding="utf-8",
    )
    (references / "notes.md").write_text("Useful reference material.\n", encoding="utf-8")

    repository = SkillsRepository(tmp_path)

    skills = repository.discover()
    assert [skill.name for skill in skills] == ["demo-skill"]
    assert repository.load_skill("demo-skill") is not None
    assert repository.read_skill_file("demo-skill", "references/notes.md") == (
        "Useful reference material.\n"
    )
    assert repository.list_skill_files("demo-skill") == "references/notes.md"


def test_rejects_invalid_frontmatter_and_path_traversal(tmp_path: Path) -> None:
    invalid_dir = tmp_path / "not-matching"
    invalid_dir.mkdir()
    (invalid_dir / "SKILL.md").write_text(
        "---\n"
        "name: different-name\n"
        "description: Invalid because folder and name differ.\n"
        "---\n",
        encoding="utf-8",
    )

    valid_dir = tmp_path / "valid-skill"
    valid_dir.mkdir()
    (valid_dir / "SKILL.md").write_text(
        "---\n"
        "name: valid-skill\n"
        "description: Valid skill for traversal tests.\n"
        "---\n",
        encoding="utf-8",
    )

    repository = SkillsRepository(tmp_path)

    assert [skill.name for skill in repository.discover()] == ["valid-skill"]
    assert repository.read_skill_file("valid-skill", "../SKILL.md").startswith("error:")
    assert repository.read_skill_file("valid-skill", "SKILL.md").startswith("error:")
