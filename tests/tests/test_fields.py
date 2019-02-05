from django.test import TestCase

from gdpr.fields import Fields
from tests.anonymizers import CustomerAnonymizer
from tests.models import Customer

LOCAL_FIELDS = ("first_name", "last_name")

BASIC_FIELDS = (
    "primary_email_address",
    ("emails", (
        "email",
    )),
)

MULTILEVEL_FIELDS = (
    ("accounts", (
        "number",
        "owner",
        ("payments", (
            "value",
            "date"
        ))
    )),
)


class TestFields(TestCase):
    def test_local_all(self):
        fields = Fields('__ALL__', Customer)
        self.assertListEqual(fields.local_fields, list(CustomerAnonymizer().fields.keys()))

    def test_local(self):
        fields = Fields(LOCAL_FIELDS, Customer)
        self.assertListEqual(fields.local_fields, list(LOCAL_FIELDS))

    def test_local_and_related(self):
        fields = Fields(BASIC_FIELDS, Customer)

        self.assertListEqual(fields.local_fields, ['primary_email_address'])
        self.assertTrue('emails' in fields.related_fields)
        self.assertListEqual(fields.related_fields['emails'].local_fields, ['email'])

    def test_multilevel_related(self):
        fields = Fields(MULTILEVEL_FIELDS, Customer)

        self.assertListEqual(fields.local_fields, [])
        self.assertTrue('accounts' in fields.related_fields)
        self.assertListEqual(fields.related_fields['accounts'].local_fields, ['number', 'owner'])
        self.assertTrue('payments' in fields.related_fields['accounts'].related_fields)
        self.assertListEqual(fields.related_fields['accounts'].related_fields['payments'].local_fields,
                             ['value', 'date'])
