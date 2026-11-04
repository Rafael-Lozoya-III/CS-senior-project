import json
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase

from accounts import views


class ProfileSuggestionViewTests(SimpleTestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def make_request(self, resume=None):
        request = self.request_factory.post(
            "/profile/suggest/",
            {"resume": resume} if resume else {},
        )
        request.user = self.user
        return request

    def test_rejects_missing_resume(self):
        with patch.object(views.StudentProfile.objects, "filter") as profile_filter:
            profile_filter.return_value.exists.return_value = True
            response = views.suggest_profile(self.make_request())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {"error": "Choose a resume first."})

    def test_rejects_non_docx_resume(self):
        resume = SimpleUploadedFile("resume.txt", b"resume")
        with patch.object(views.StudentProfile.objects, "filter") as profile_filter:
            profile_filter.return_value.exists.return_value = True
            response = views.suggest_profile(self.make_request(resume))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Upload a Word document (.docx) resume."},
        )

    def test_returns_only_valid_catalog_suggestions(self):
        resume = SimpleUploadedFile("resume.docx", b"resume")
        skill = SimpleNamespace(id="skill-1")
        interest = SimpleNamespace(id="interest-1")

        @contextmanager
        def resume_context(_resume):
            yield "Resume text"

        with (
            patch.object(views.StudentProfile.objects, "filter") as profile_filter,
            patch("accounts.ai_profile.resume_context", resume_context),
            patch("accounts.ai_profile.build_profile_assistant", return_value=object()),
            patch(
                "agents.Runner.run_sync",
                return_value=SimpleNamespace(
                    final_output=json.dumps(
                        {
                            "skills": [
                                {"id": "skill-1", "level": 2},
                                {"id": "unknown", "level": 2},
                                {"id": "skill-1", "level": 9},
                            ],
                            "interests": ["interest-1", "unknown"],
                        }
                    )
                ),
            ),
            patch("accounts.models.Skill.objects.all", return_value=[skill]),
            patch("accounts.models.Interest.objects.all", return_value=[interest]),
        ):
            profile_filter.return_value.exists.return_value = True
            response = views.suggest_profile(self.make_request(resume))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "skills": [{"id": "skill-1", "level": 2}],
                "interests": ["interest-1"],
            },
        )

# Create your tests here.
