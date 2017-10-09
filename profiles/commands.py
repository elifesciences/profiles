from flask_script import Command
from profiles.models import Name, Profile


class ClearCommand(Command):
    NAME = 'clear'

    def __init__(self, *repositories):
        super(ClearCommand, self).__init__()
        self.repositories = repositories

    # weird decoration made by the superclass that wraps this method
    # not going to lose sleep over this for now,
    # let's see whether we get more commands
    # and we keep flask_script in the long term
    # pylint: disable=method-hidden
    def run(self):
        for each in self.repositories:
            each.clear()


def update_profile_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    _update_name_from_orcid_record(profile, orcid_record)
    _update_email_addresses_from_orcid_record(profile, orcid_record)


def _update_name_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    if 'name' in orcid_record.get('person', {}):
        given_name = orcid_record['person']['name']['given-names']['value']
        family_name = orcid_record['person']['name']['family-name']['value']

        profile.name = Name('{} {}'.format(given_name, family_name),
                            '{}, {}'.format(family_name, given_name))


def _update_email_addresses_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    orcid_emails = orcid_record.get('person', {}).get('emails', {}).get('email', {})
    orcid_emails = list(filter(lambda x: x['verified'], orcid_emails))

    for email in profile.email_addresses:
        found = False
        for orcid_email in orcid_emails:
            if orcid_email['email'] == email.email:
                found = True
                break
        if not found:
            profile.remove_email_address(email.email)

    for orcid_email in orcid_emails:
        profile.add_email_address(orcid_email['email'], orcid_email['primary'],
                                  orcid_email['visibility'] != 'PUBLIC')
