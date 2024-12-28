"""Test data for teams-related API responses"""

# Basic teams list
BASIC_TEAMS = {
    "teams": [
        {"id": "TEAM1", "name": "Engineering"},
        {"id": "TEAM2", "name": "Product"}
    ]
}

# Team with members
TEAM_WITH_MEMBERS = {
    "teams": [{
        "id": "TEAM3",
        "name": "Leadership",
        "members": [
            {"id": "USER1", "name": "CEO"},
            {"id": "USER2", "name": "CTO"}
        ]
    }]
}

# Test cases mapping
TEAMS_TEST_CASES = [
    ("basic_teams", BASIC_TEAMS),
    ("team_with_members", TEAM_WITH_MEMBERS)
]
