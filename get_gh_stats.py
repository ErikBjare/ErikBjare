"""
Get GitHub stats for a user or organization.

Like:
 - followers
 - following
 - number of repos
 - number of stars
 - number of forks
 - number of watchers
"""

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import json

import requests


@dataclass
class UserStats:
    followers: int
    following: int
    repos: int
    stargazers: int

    def append_to_csv(self, filename):
        filename = Path(filename)
        if not filename.exists():
            with open(filename, 'w') as f:
                f.write('date,followers,following,repos,stars\n')
        with open(filename, "a") as f:
            now = datetime.now()
            f.write(f"{now},{self.followers},{self.following},{self.repos},{self.stars}\n")


def get_user_stats(username: str) -> UserStats:
    """Get stats for a user."""
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error getting stats for {username}: {response.status_code}")
    data = json.loads(response.text)

    repostats = get_repostats(username)
    print(data)
    return UserStats(
        followers=data['followers'],
        following=data['following'],
        repos=data['public_repos'],
        # NOTE: this is not all stars, as repostats only contains the first N repos
        stargazers=sum(repo['stargazers_count'] for repo in repostats),
    )


def get_repostats(username: str) -> dict:
    """Get stats for a user."""
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error getting stats for {username}: {response.status_code}")
    data = json.loads(response.text)

    print(data)
    return data


def main():
    """Get stats for a user."""
    username = "ErikBjare"
    stats = get_user_stats(username)
    stats.append_to_csv("user-stats.csv")


if __name__ == "__main__":
    main()
