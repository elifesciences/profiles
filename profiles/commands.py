from iso3166 import countries
from pendulum import create as date

from profiles.models import Affiliation, Name, Profile


def update_profile_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    _update_name_from_orcid_record(profile, orcid_record)
    _update_affiliations_from_orcid_record(profile, orcid_record)
    _update_email_addresses_from_orcid_record(profile, orcid_record)


def _update_name_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    if 'name' in orcid_record.get('person', {}):
        given_name = orcid_record['person']['name']['given-names']['value']
        family_name = orcid_record['person']['name']['family-name']['value']

        profile.name = Name('{} {}'.format(given_name, family_name),
                            '{}, {}'.format(family_name, given_name))


def _update_affiliations_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    def create_affiliation(properties: dict) -> Affiliation:
        organization = properties['organization']
        address = organization['address']

        return Affiliation(countries.get(address['country']), organization['name'],
                           properties.get('department-name'), address.get('city'),
                           address.get('region'), properties['visibility'] != 'PUBLIC')

    def filter_past(properties: dict) -> bool:
        if 'end-date' in properties:
            return not date(properties['end-date']['year'], properties['end-date']['month'],
                            properties['end-date']['day']).is_past()

        return True

    orcid_affiliations = orcid_record.get('activities-summary', {}).get('employments', {}).get(
        'employment-summary', {})
    orcid_affiliations = filter(filter_past, orcid_affiliations)
    orcid_affiliations = list(map(create_affiliation, orcid_affiliations))

    for affiliation in profile.affiliations:
        if affiliation not in orcid_affiliations:
            profile.remove_affiliation(affiliation)

    for index, orcid_affiliation in enumerate(orcid_affiliations):
        profile.add_affiliation(orcid_affiliation, index)


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
