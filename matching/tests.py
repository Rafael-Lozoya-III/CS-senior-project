from django.contrib.auth.models import User
from django.test import TestCase
import factory

from accounts.models import (
    Project,
    ProjectSkillRequirement,
    Skill,
    StudentProfile,
    StudentSkill,
)
from matching.services import rank_candidates, rank_project_candidates


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")


class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill

    name = factory.Sequence(lambda n: f"Skill {n}")


class StudentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentProfile

    user = factory.SubFactory(UserFactory)


class StudentSkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentSkill

    student = factory.SubFactory(StudentProfileFactory)
    skill = factory.SubFactory(SkillFactory)
    level = 1


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    title = factory.Sequence(lambda n: f"Project {n}")
    description = "Test project"
    creator = factory.SubFactory(UserFactory)


class ProjectSkillRequirementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectSkillRequirement

    project = factory.SubFactory(ProjectFactory)
    skill = factory.SubFactory(SkillFactory)
    min_level = 1
    is_core = False


class MatchingAlgorithmTests(TestCase):
    def test_scores_core_and_supporting_skills(self):
        project = ProjectFactory()
        python = SkillFactory(name="Python")
        design = SkillFactory(name="Design")
        candidate = StudentProfileFactory()
        StudentSkillFactory(student=candidate, skill=python, level=3)
        StudentSkillFactory(student=candidate, skill=design, level=3)

        ProjectSkillRequirementFactory(
            project=project,
            skill=python,
            min_level=1,
            is_core=True,
        )
        ProjectSkillRequirementFactory(
            project=project,
            skill=design,
            min_level=2,
        )

        result = rank_candidates(
            [candidate],
            project.skill_requirements.select_related("skill"),
        )[0]

        self.assertTrue(result.eligible)
        self.assertEqual(result.score, 14)
        self.assertEqual(result.supporting_total, 1)
        self.assertEqual(result.matched_supporting, ["Design"])
        self.assertEqual(result.missing_core, [])

    def test_missing_core_makes_candidate_ineligible_and_ranks_eligible_first(self):
        project = ProjectFactory()
        python = SkillFactory(name="Python")
        sql = SkillFactory(name="SQL")
        design = SkillFactory(name="Design")
        eligible = StudentProfileFactory()
        ineligible = StudentProfileFactory()

        StudentSkillFactory(student=eligible, skill=python, level=1)
        StudentSkillFactory(student=eligible, skill=sql, level=1)
        StudentSkillFactory(student=ineligible, skill=design, level=3)

        ProjectSkillRequirementFactory(
            project=project, skill=python, is_core=True
        )
        ProjectSkillRequirementFactory(
            project=project, skill=sql, is_core=True
        )
        ProjectSkillRequirementFactory(project=project, skill=design)

        results = rank_candidates(
            [ineligible, eligible],
            project.skill_requirements.select_related("skill"),
        )

        self.assertEqual(
            [result.student for result in results],
            [eligible, ineligible],
        )
        self.assertTrue(results[0].eligible)
        self.assertFalse(results[1].eligible)
        self.assertEqual(results[1].missing_core, ["Python", "SQL"])
        self.assertEqual(results[1].score, 14)

    def test_team_coverage_removes_supporting_skill_and_excludes_member(self):
        project = ProjectFactory()
        design = SkillFactory(name="Design")
        research = SkillFactory(name="Research")
        member = StudentProfileFactory()
        candidate = StudentProfileFactory()

        StudentSkillFactory(student=member, skill=design, level=2)
        StudentSkillFactory(student=candidate, skill=design, level=3)
        StudentSkillFactory(student=candidate, skill=research, level=2)

        ProjectSkillRequirementFactory(
            project=project,
            skill=design,
            min_level=2,
        )
        ProjectSkillRequirementFactory(project=project, skill=research)

        results = rank_candidates(
            [member, candidate],
            project.skill_requirements.select_related("skill"),
            team_members=[member],
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].student, candidate)
        self.assertEqual(results[0].score, 12)
        self.assertEqual(results[0].supporting_total, 1)
        self.assertEqual(results[0].matched_supporting, ["Research"])

    def test_project_wrapper_uses_project_requirements(self):
        project = ProjectFactory()
        python = SkillFactory(name="Python")
        candidate = StudentProfileFactory()
        StudentSkillFactory(student=candidate, skill=python, level=2)
        ProjectSkillRequirementFactory(
            project=project,
            skill=python,
            min_level=2,
            is_core=True,
        )

        results = rank_project_candidates(project, [candidate])

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].eligible)
        self.assertEqual(results[0].score, 0)
        self.assertEqual(results[0].missing_core, [])
