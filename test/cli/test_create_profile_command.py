from profiles.cli import CreateProfileCommand
from profiles.repositories import SQLAlchemyProfiles

def test_can_create_profile_via_command(profiles: SQLAlchemyProfiles) -> None:
    CreateProfileCommand(profiles, 'Test User', 'test@test.com')
    assert profiles.get_by_email_address('test@test.com')

def test_can_run_command_multiple_times(profiles: SQLAlchemyProfiles) -> None:
    for _ in range(5):
        CreateProfileCommand(profiles, 'Test User', 'test@test.com')
    assert len(profiles.list()) == 1
