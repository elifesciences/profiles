import logging
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from iso3166 import countries
import jmespath

from profiles.exceptions import ProfileNotFound
from profiles.models import Address, Affiliation, Date, Name, Profile, db
from profiles.orcid import VISIBILITY_PUBLIC
from profiles.repositories import SQLAlchemyProfiles

LOGGER = logging.getLogger(__name__)


def update_profile_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    try:
        LOGGER.info('Updating profile %s with ORCID record %s', profile.id, orcid_record.get('path'))
        _update_name_from_orcid_record(profile, orcid_record)
        _update_affiliations_from_orcid_record(profile, orcid_record)
        _update_email_addresses_from_orcid_record(profile, orcid_record)
    except IntegrityError:
        # lsh@2023-02-22: we've had three cases of an update failing, the transaction not being rolled back and
        # subsequent incoming updates failing because of this db.session's state.
        # either it's an orcid record with data that triggers this, or some race condition between two incoming updates
        # for the same profile, as db.session appears to be shared between all requests.
        # - https://github.com/elifesciences/issues/issues/8275
        LOGGER.exception("uncaught database exception updating profile from orcid record, rolling session transaction back", extra={"orcid_record": orcid_record})
        # hopefully prevents other requests from failing
        db.session.rollback()
        # punt error downstream
        raise

def extract_email_addresses(orcid_record: dict, only_verified: bool = True) -> List[dict]:
    orcid_emails = jmespath.search('person.emails.email[*]', orcid_record) or []

    if only_verified:
        orcid_emails = list(filter(lambda x: x['verified'], orcid_emails))

    return orcid_emails


def _update_name_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    given_name = jmespath.search('person.name."given-names".value', orcid_record)
    family_name = jmespath.search('person.name."family-name".value', orcid_record)

    if given_name and family_name:
        profile.name = Name('{} {}'.format(given_name, family_name),
                            '{}, {}'.format(family_name, given_name))
    elif given_name:
        profile.name = Name(given_name, given_name)
    elif family_name:
        profile.name = Name(family_name, family_name)


def _update_affiliations_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    orcid_affiliations = jmespath.search('"activities-summary".employments."employment-summary"[*]',
                                         orcid_record) or []

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
            starts=_convert_orcid_date(orcid_affiliation.get('start-date') or {}),
            ends=_convert_orcid_date(orcid_affiliation.get('end-date') or {}),
            restricted=orcid_affiliation['visibility'] != VISIBILITY_PUBLIC,
        )
        profile.add_affiliation(affiliation, index)
        found_affiliation_ids.add(affiliation.id)

    for affiliation in profile.affiliations:
        if affiliation.id not in found_affiliation_ids:
            profile.remove_affiliation(affiliation.id)


def _update_email_addresses_from_orcid_record(profile: Profile, orcid_record: dict) -> None:
    orcid_email_dicts = extract_email_addresses(orcid_record)
    profiles = SQLAlchemyProfiles(db)

    for index, email_dict in enumerate(orcid_email_dicts):
        email = email_dict.get('email')
        try:
            email_profile = profiles.get_by_email_address(email)
        except ProfileNotFound:
            continue

        if email_profile.id != profile.id:
            message = ('Profile %s is trying to add email address %s but this '
                       'email is associated with profile %s which violates '
                       'unique constraint for email addresses' %
                       (profile.id, email, email_profile.id))
            LOGGER.error(message)
            del orcid_email_dicts[index]

    for email in profile.email_addresses:
        found = False
        for orcid_email in orcid_email_dicts:
            if orcid_email['email'] == email.email:
                found = True
                break
        if not found:
            profile.remove_email_address(email.email)

    for orcid_email in orcid_email_dicts:
        profile.add_email_address(orcid_email['email'], orcid_email['primary'],
                                  orcid_email['visibility'] != VISIBILITY_PUBLIC)


def _convert_orcid_date(orcid_date: dict) -> Optional[Date]:
    if 'year' in orcid_date:
        year = int(orcid_date['year']['value'])
        month = int(orcid_date['month']['value']) if orcid_date.get('month') else None
        day = int(orcid_date['day']['value']) if orcid_date.get('day') else None
        try:
            return Date(year, month, day)
        except ValueError as exception:
            # lsh@2022-12-07: downgraded `.error` to `.debug` for a class of bad data.
            # we're getting 10-90 of these a day and they're just noise.
            # - https://github.com/elifesciences/issues/issues/7974
            msg = '%s: %s' % (exception, (year, month, day))
            if str(exception) == "day is out of range for month":
                LOGGER.debug(msg)
            else:
                LOGGER.error(msg)
