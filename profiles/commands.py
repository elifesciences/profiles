from typing import List, Optional

from iso3166 import countries

from profiles.models import Address, Affiliation, Date, Name, Profile
from profiles.orcid import VISIBILITY_PUBLIC


def update_profile_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    _update_name_from_orcid_record(profile, orcid_record)
    _update_affiliations_from_orcid_record(profile, orcid_record)
    _update_email_addresses_from_orcid_record(profile, orcid_record)


def extract_email_addresses(orcid_record: dict, only_verified: bool = True) -> List[dict]:
    orcid_emails = orcid_record.get('person', {}).get('emails', {}).get('email', {})

    if only_verified:
        orcid_emails = list(filter(lambda x: x['verified'], orcid_emails))

    return orcid_emails


def _update_name_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    if 'name' in orcid_record.get('person', {}):
        given_name = orcid_record['person']['name']['given-names']['value']
        family_name = orcid_record['person']['name']['family-name']['value']

        profile.name = Name('{} {}'.format(given_name, family_name),
                            '{}, {}'.format(family_name, given_name))


def _update_affiliations_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    orcid_affiliations = orcid_record.get('activities-summary', {}).get('employments', {}).get(
        'employment-summary', {})

    found_affiliation_ids = set()
    for index, orcid_affiliation in enumerate(orcid_affiliations):
        organization = orcid_affiliation['organization']
        address = organization['address']

        affiliation = Affiliation(
            affiliation_id=str(orcid_affiliation['put-code']),
            department=orcid_affiliation.get('department-name'),
            organisation=organization['name'],
            address=Address(
                city=address['city'],
                region=address.get('region'),
                country=countries.get(address['country']),
            ),
            starts=_convert_orcid_date(orcid_affiliation['start-date']),
            ends=_convert_orcid_date(orcid_affiliation.get('end-date') or {}),
            restricted=orcid_affiliation['visibility'] != VISIBILITY_PUBLIC,
        )
        profile.add_affiliation(affiliation, index)
        found_affiliation_ids.add(affiliation.id)

    for affiliation in profile.affiliations:
        if affiliation.id not in found_affiliation_ids:
            profile.remove_affiliation(affiliation.id)


def _update_email_addresses_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    orcid_emails = extract_email_addresses(orcid_record)

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
                                  orcid_email['visibility'] != VISIBILITY_PUBLIC)


def _convert_orcid_date(orcid_date: dict) -> Optional[Date]:
    if 'year' in orcid_date:
        year = int(orcid_date['year']['value'])
        month = int(orcid_date['month']['value']) if orcid_date.get('month') else None
        day = int(orcid_date['day']['value']) if orcid_date.get('day') else None

        return Date(year, month, day)
