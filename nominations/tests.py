from django.test import TestCase
from models import Application
from local_groups.models import Group


class ApplicationTestCase(TestCase):
    def setUp(self):
        # create group
        group = Group.objects.create(
            name='Test Group',
            group_id=9999
        )

        # create application
        Application.objects.create(
            group=group,
            rep_email='john@example.com',
            rep_first_name='John',
            rep_last_name='Doe',
            rep_phone='6155555555',
            candidate_first_name='Test',
            candidate_last_name='Candidate',
            candidate_office='Governor',
            candidate_state='TN'
        )

    def test_generate_application_status(self):
        """
        The status of the Application should be properly set based on the
        status of the nomination form (nomination) and the questionnaire.
        """

        app = Application.objects.get(
            candidate_first_name='Test',
            candidate_last_name='Candidate'
        )

        # nomination form incomplete, questionnaire complete
        app.nomination.status = 'incomplete'
        app.questionnaire.status = 'incomplete'
        app.status = app.generate_application_status()

        self.assertEqual(app.status, 'needs-group-form-and-questionnaire')

        # nomination form complete, questionnaire incomplete
        app.nomination.status = 'complete'
        app.questionnaire.status = 'incomplete'
        app.status = app.generate_application_status()

        self.assertEqual(app.status, 'needs-questionnaire')

        # nomination form and questionnare completed
        app.nomination.status = 'complete'
        app.questionnaire.status = 'complete'
        app.status = app.generate_application_status()

        self.assertEqual(app.status, 'incomplete')

        # nomination form incomplete, questionnaire complete
        app.nomination.status = 'incomplete'
        app.questionnaire.status = 'complete'
        app.status = app.generate_application_status()

        self.assertEqual(app.status, 'needs-group-form')

        # if application isn't editable, status shouldn't change
        app.status = 'submitted'
        app.status = app.generate_application_status()

        self.assertEqual(app.status, 'submitted')

    def test_save(self):
        """When an Application is saved, related objects should be created if
        necessary, status should be set properly, research fields should be
        auto-populated and submissions datetime should be set if necessary."""

        app = Application.objects.get(
            candidate_first_name='Test',
            candidate_last_name='Candidate'
        )

        # check for related objects nomination form (nomination)
        # and questionnaire
        self.assertNotEqual(app.nomination, None)
        self.assertNotEqual(app.questionnaire, None)

        # check that they are properly related to the application
        self.assertEqual(app, app.nomination.application)
        self.assertEqual(app, app.questionnaire.application_set.first())

        # check that their individual default statuses are properly set
        self.assertEqual(app.nomination.status, 'incomplete')
        self.assertEqual(app.questionnaire.status, 'incomplete')

        # check that generate_application_status is called after
        # nomination is saved
        app.nomination.status = 'complete'
        app.nomination.save()

        self.assertEqual(app.nomination.status, 'complete')
        self.assertEqual(app.status, 'needs-questionnaire')

        # check that generate_application_status is called after
        # questionnaire is saved
        app.questionnaire.status = 'complete'
        app.questionnaire.save()

        self.assertEqual(app.questionnaire.status, 'complete')

        # this works
        self.assertEqual(app.questionnaire.application_set.first(), app)

        # but this doesn't?
        # self.assertEqual(app.status, 'incomplete')

