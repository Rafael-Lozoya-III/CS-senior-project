from dataclasses import dataclass, field
from accounts.models import Skill, StudentSkill

SUPPORTING_BASE = 10
SUPPORTING_LEVEL_BONUS = 2
CORE_LEVEL_BONUS = 1

@dataclass
class Requirement:
    skill: Skill
    min_level: int = 1
    is_core: bool = False

@dataclass
class MatchResult:
    student: object
    eligible: bool
    score: int
    supporting_total: int = 0
    missing_core: list = field(default_factory = list)
    matched_supporting: list = field(default_factory=list)

    @property
    def label(self):
        if not self.eligible:
            return "Missing core: " + ", ".join(self.missing_core)
        return (
            f"Meets all core skills, fits "
            f"{len(self.matched_supporting)} of {self.supporting_total} supporting"
        )

def _levels_by_student(students):
    """One query: {student_id: {skill_id: level}}."""
    levels = {}
    for row in StudentSkill.objects.filter(student__in=students):
        levels.setdefault(row.student_id, {})[row.skill_id] = row.level
    return levels

def _open_supporting(requirements, member_levels):
    """Supporting requirements nobody on the team covers yet."""
    open_reqs = []
    for req in requirements:
        if req.is_core:
            continue
        covered = any(
            lv.get(req.skill.pk, 0) >= req.min_level for lv in member_levels
        )
        if not covered:
            open_reqs.append(req)
    return open_reqs

def _score(student, student_levels, requirements, open_supporting):
    score = 0
    missing_core = []
    for req in requirements:
        if not req.is_core:
            continue
        level = student_levels.get(req.skill.pk, 0)
        if level >= req.min_level:
            score += CORE_LEVEL_BONUS * (level - req.min_level)
        else:
            missing_core.append(req.skill.name)

    matched = []
    for req in open_supporting:
        level = student_levels.get(req.skill.pk, 0)
        if level >= req.min_level:
            score += SUPPORTING_BASE + SUPPORTING_LEVEL_BONUS * (level - req.min_level)
            matched.append(req.skill.name)

    return MatchResult(
        student=student,
        eligible=not missing_core,
        score=score,
        supporting_total=len(open_supporting),
        missing_core=missing_core,
        matched_supporting=matched,
    )

def rank_candidates(candidates, requirements, team_members=()):
    team_members = list(team_members)
    member_ids = {m.pk for m in team_members}
    candidates = [c for c in candidates if c.pk not in member_ids]
    
    levels = _levels_by_student(candidates + team_members)
    member_levels = [levels.get(m.pk, {}) for m in team_members]
    open_supporting = _open_supporting(requirements, member_levels)

    results = [
        _score(c, levels.get(c.pk, {}), requirements, open_supporting)
        for c in candidates
    ]
    results.sort(key=lambda r: (not r.eligible, -r.score, str(r.student)))
    return results

def rank_teams_for_student(student, teams):
    scored = []
    for team, requirements, members in teams:
        results = rank_candidates([student], requirements, members)
        if results:
            scored.append((team, results[0]))
    scored.sort(key=lambda pair: (not pair[1].eligible, -pair[1].score))
    return scored