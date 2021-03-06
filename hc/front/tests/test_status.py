from hc.api.models import Check
from hc.test import BaseTestCase


class MyChecksTestCase(BaseTestCase):

    def setUp(self):
        super(MyChecksTestCase, self).setUp()
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.tags = "foo"
        self.check.save()

    def test_it_works(self):
        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/teams/alice/checks/status/")
        self.assertEqual(r.status_code, 200)
        doc = r.json()

        self.assertEqual(doc["tags"]["foo"], "up")

        detail = doc["details"][0]
        self.assertEqual(detail["code"], str(self.check.code))
        self.assertEqual(detail["status"], "new")
        self.assertIn("Never", detail["last_ping"])

    def test_it_allows_cross_team_access(self):
        self.bobs_profile.current_team = None
        self.bobs_profile.save()

        self.client.login(username="bob@example.org", password="password")
        r = self.client.get("/teams/alice/checks/status/")
        self.assertEqual(r.status_code, 200)

    def test_it_checks_ownership(self):
        self.bobs_profile.current_team = None
        self.bobs_profile.save()

        self.client.login(username="charlie@example.org", password="password")
        r = self.client.get("/teams/alice/checks/status/")
        self.assertEqual(r.status_code, 404)
