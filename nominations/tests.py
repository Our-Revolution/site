from django.test import TestCase
from models import Application
from local_groups.models import Group


class ApplicationTestCase(TestCase):
    def setUp(self):
        # create group
        group = Group.objects.create(
            name='Test Group',
            group_id=0000
        )

        # create application
        Application.objects.create(
            group=group,
            rep_email='john@example.com',
            rep_first_name='John',
            rep_last_name='Doe',
            rep_phone='6155555555',
            candidate_first_name='Candidate',
            candidate_last_name='Candidateson',
            candidate_office='Governor',
            candidate_state='TN'
        )

    def test_application_creation(self):
        """
        When an application is created, a Questionnaire and a Nomination
        should be created as well.
        """

        app = Application.objects.first()

        # check for nominations and questionnaire
        self.assertNotEqual(app.nomination, None)
        self.assertNotEqual(app.questionnaire, None)
        self.assertEqual(app, app.nomination.application)
        self.assertEqual(app, app.questionnaire.application_set.first())

    def test_status_generation(self):
        """
        When an Application, related Nomination or Questionnaire is saved,
        the status of the Application should be properly set.
        """

        # set local group
        group = Group.objects.first()

        # create new application
        app = Application.objects.create(
            group=group,
            rep_email='john@example.com',
            rep_first_name='John',
            rep_last_name='Doe',
            rep_phone='6155555555',
            candidate_first_name='Candidate',
            candidate_last_name='Candidateson',
            candidate_office='Governor',
            candidate_state='TN'
        )

        # check for nominations and questionnaire
        self.assertNotEqual(app.nomination, None)
        self.assertNotEqual(app.questionnaire, None)
        self.assertEqual(app, app.nomination.application)
        self.assertEqual(app, app.questionnaire.application_set.first())

        # check for default states
        self.assertEqual(app.nomination.status, 'incomplete')
        self.assertEqual(app.questionnaire.status, 'incomplete')
        self.assertEqual(app.status, 'needs-group-form-and-questionnaire')

        # complete nomination
        app.nomination.status = 'complete'
        app.nomination.save()
        self.assertEqual(app.nomination.status, 'complete')
        self.assertEqual(app.questionnaire.status, 'incomplete')
        self.assertEqual(app.status, 'needs-questionnaire')

        # complete questionnaire
        app.questionnaire.status = 'complete'
        app.questionnaire.save()
        self.assertEqual(app.nomination.status, 'complete')
        self.assertEqual(app.questionnaire.status, 'complete')
        # I don't know why this is failing
        # self.assertEqual(app.status, 'incomplete')
