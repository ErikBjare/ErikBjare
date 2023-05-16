import requests
import csv
import os
import time
from typing import List, Dict
from time import sleep


def fetch_github_events(username: str, last_event_timestamp: str = None, max_pages: int = 10) -> List[Dict]:
    page = 1
    events: list[dict] = []

    while page <= max_pages:
        url = f"https://api.github.com/users/{username}/events?page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch events for user {username}: {response.status_code} - {response.text}")

        remaining_requests = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))

        json_data = response.json()
        if not json_data:
            break

        for event in json_data:
            timestamp = event["created_at"]

            if last_event_timestamp and timestamp <= last_event_timestamp:
                return events

            event = {
                "timestamp": timestamp,
                "user": username,
                "data": {
                    "desc": f"{event['type']} on {event['repo']['name']}",
                    "url": f"https://github.com/{event['repo']['name']}"
                }
            }
            events.append(event)

        page += 1
        if remaining_requests == 0:
            sleep_time = reset_time - time.time()
            if sleep_time > 0:
                sleep(sleep_time)

    return events


def read_last_event_timestamp(file_path: str) -> str | None:
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        reader = csv.reader(f)
        return next(reversed(list(reader)))[0]


def write_events_to_csv(file_path: str, events: List[Dict]):
    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline='') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "user", "desc", "url"])

        for event in events:
            writer.writerow([event["timestamp"], event["user"], event["data"]["desc"], event["data"]["url"]])


def main():
    # Replace 'username' with the desired GitHub username
    github_user = 'ErikBjare'
    csv_file = 'events.csv'

    last_event_timestamp = read_last_event_timestamp(csv_file)
    events = fetch_github_events(github_user, last_event_timestamp)

    if events:
        write_events_to_csv(csv_file, events)

        for event in events:
            print(event)
    else:
        print("No new events found.")


if __name__ == "__main__":
    main()
