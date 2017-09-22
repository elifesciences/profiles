import random
import string
from datetime import datetime, timedelta

from profiles.models import Profile


def expires_at(expires_in: int) -> datetime:
    return datetime.utcnow() + timedelta(seconds=expires_in)


def generate_random_string(length: int, chars: str = string.ascii_letters + string.digits) -> str:
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def remove_none_values(items: dict) -> dict:
    return dict(filter(lambda item: item[1] is not None, items.items()))


def update_profile_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    _update_name_from_orcid_record(profile, orcid_record)
    _update_email_addresses_from_orcid_record(profile, orcid_record)


def _update_name_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    if 'name' in orcid_record.get('person', {}):
        profile.name = '{} {}'.format(orcid_record['person']['name']['given-names']['value'],
                                      orcid_record['person']['name']['family-name']['value'])


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
