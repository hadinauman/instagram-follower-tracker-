import instaloader
import json
import os
from datetime import datetime
import time
import argparse
from tqdm import tqdm

# parse command line arguments
parser = argparse.ArgumentParser(description='Instagram Follower Tracker')
parser.add_argument('username', nargs='?', help='Instagram username to track')
parser.add_argument('--login', action='store_true', help='Force login even if session exists')
args = parser.parse_args()

# create object
L = instaloader.Instaloader()

# get username from args or prompt
if args.username:
    USER = args.username
else:
    USER = input("Enter Instagram username: ")

# login
session_loaded = False
if not args.login:
    try:
        # try to load saved session first
        L.load_session_from_file(USER)
        print(f"Session loaded successfully for @{USER}!")
        session_loaded = True
    except FileNotFoundError:
        pass

if not session_loaded:
    # no saved session, need to log in
    print("Logging in...")
    try:
        L.interactive_login(USER)
        L.save_session_to_file()
        print("Login successful!")
    except instaloader.exceptions.BadCredentialsException:
        print("Error: Invalid username or password.")
        exit(1)
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("Error: Two-factor authentication required. Please complete 2FA.")
        exit(1)
    except Exception as e:
        print(f"Login error: {e}")
        exit(1)

# get profile
try:
    profile = instaloader.Profile.from_username(L.context, USER)
except instaloader.exceptions.ProfileNotExistsException:
    print(f"Error: Profile '{USER}' does not exist.")
    exit(1)
except Exception as e:
    print(f"Error loading profile: {e}")
    exit(1)

# get current followers with retry logic and progress bar
print(f"Fetching followers for @{USER} (this may take a while)...")
max_retries = 3
retry_delay = 60  # seconds

for attempt in range(max_retries):
    try:
        # fetch followers with progress bar
        followers_iterator = profile.get_followers()
        current_followers = set()

        # get total follower count for progress bar
        total_followers = profile.followers

        with tqdm(total=total_followers, desc="Fetching followers", unit="follower") as pbar:
            for follower in followers_iterator:
                current_followers.add(follower.username)
                pbar.update(1)

        print(f"Successfully fetched {len(current_followers)} followers!")
        break
    except instaloader.exceptions.ConnectionException as e:
        error_str = str(e)
        if "429" in error_str or "rate limit" in error_str.lower() or "401" in error_str or "wait a few minutes" in error_str.lower():
            if attempt < max_retries - 1:
                print(f"Rate limit hit. Waiting {retry_delay} seconds before retry {attempt + 2}/{max_retries}...")
                time.sleep(retry_delay)
                retry_delay *= 2  # exponential backoff
            else:
                print("\nError: Rate limit exceeded.")
                print("Instagram is temporarily blocking requests.")
                print("Please wait 30-60 minutes before trying again.")
                exit(1)
        else:
            print(f"Connection error: {e}")
            exit(1)
    except instaloader.exceptions.QueryReturnedBadRequestException:
        print("Error: Bad request. Your account may be restricted or flagged.")
        exit(1)
    except Exception as e:
        print(f"Error fetching followers: {e}")
        exit(1)

if os.path.exists("previous_followers.json"):
    # load previous followers
    try:
        with open("previous_followers.json", "r") as f:
            data = json.load(f)
            previous_followers = set(data["followers"])
            last_check = data["timestamp"]
    except json.JSONDecodeError:
        print("Error: Corrupted previous_followers.json file. Starting fresh.")
        previous_followers = set()
        last_check = None
    except Exception as e:
        print(f"Error reading previous data: {e}")
        exit(1)

    # compares current and previous followers
    unfollowers = previous_followers - current_followers

    #display results
    if unfollowers:
        print("Users who have unfollowed you since the last check:")
        for user in unfollowers:
            print(user)
    else:
        print("No users have unfollowed you since the last check.")

    new_followers = current_followers - previous_followers

    # display new followers
    if new_followers:
        print("\nNew followers since the last check:")
        for user in new_followers:
            print(user)

else:
    print("No previous follower data found. Creating new record.")

# save current followers with timestamp
try:
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "followers": list(current_followers)
    }
    with open("previous_followers.json", "w") as f:
        json.dump(data, f, indent=2)
except Exception as e:
    print(f"Error saving follower data: {e}")
    exit(1)

# display last check time
if os.path.exists("previous_followers.json") and 'last_check' in locals():
    print(f"Last check was at: {last_check}")
print("Follower data has been updated.")
