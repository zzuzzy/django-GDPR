from dateutil.relativedelta import relativedelta

from gdpr.purposes.default import AbstractPurpose

# SLUG can be any length up to 100 characters
FIRST_N_LAST_NAME_SLUG = "FNL"
EMAIL_SLUG = "EML"
PAYMENT_VALUE_SLUG = "PVL"
ACCOUNT_SLUG = "ACC"
ACCOUNT_N_PAYMENT_SLUG = "ACP"
ADDRESS_SLUG = "ADD"
CONTACT_FORM_SLUG = "CTF"
EVERYTHING_SLUG = "EVR"


class FirstNLastNamePurpose(AbstractPurpose):
    """Store First & Last name for 10 years."""
    name = "retain due to internet archive"
    slug = FIRST_N_LAST_NAME_SLUG
    expiration_timedelta = relativedelta(years=10)
    fields = ("first_name", "last_name")


class EmailsPurpose(AbstractPurpose):
    """Store emails for 5 years."""
    name = "retain due to over cat overlords"
    slug = EMAIL_SLUG
    expiration_timedelta = relativedelta(years=5)
    fields = (
        "primary_email_address",
        ("emails", (
            "email",
        )),
    )


class PaymentValuePurpose(AbstractPurpose):
    name = "retain due to Foo bar"
    slug = PAYMENT_VALUE_SLUG
    expiration_timedelta = relativedelta(months=6)
    fields = (
        ("accounts", (
            ("payments", (
                "value",
            )),
        )),
    )


class AccountPurpose(AbstractPurpose):
    name = "retain due to Lorem ipsum"
    slug = ACCOUNT_SLUG
    expiration_timedelta = relativedelta(years=2)
    fields = (
        ("accounts", (
            "number",
            "owner"
        )),
    )


class AccountsAndPaymentsPurpose(AbstractPurpose):
    name = "retain due to Gandalf"
    slug = ACCOUNT_N_PAYMENT_SLUG
    expiration_timedelta = relativedelta(years=3)
    fields = (
        ("accounts", (
            "number",
            "owner",
            ("payments", (
                "value",
                "date"
            )),
        )),
    )


class AddressPurpose(AbstractPurpose):
    name = "retain due to why not?"
    slug = ADDRESS_SLUG
    expiration_timedelta = relativedelta(years=1)
    fields = (
        ("addresses", (
            "street",
            "house_number"
        )),
    )


class EverythingPurpose(AbstractPurpose):
    name = "retain due to Area 51"
    slug = EVERYTHING_SLUG
    expiration_timedelta = relativedelta(years=51)
    fields = (
        "__ALL__",
        ("addresses", "__ALL__"),
        ("accounts", (
            "__ALL__",
            ("payments", (
                "__ALL__",
            ))
        )),
        ("emails", (
            "__ALL__",
        )),
    )


class ContactFormPurpose(AbstractPurpose):
    name = "retain due to mailing campaign"
    slug = CONTACT_FORM_SLUG
    expiration_timedelta = relativedelta(months=1)
    fields = "__ALL__"
