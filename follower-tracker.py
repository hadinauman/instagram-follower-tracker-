import instaloader
import json
import os

#create object
L = instaloader.Instaloader()

#login
USER = input("Enter Instagram username: ")
L.interactive_login(USER)
try:
      L.load_session_from_file(USER)
except FileNotFoundError:
      L.interactive_login(USER)
      L.save_session_to_file(USER)

#get profile
profile = instaloader.Profile.from_username(L.context, USER)

#get current followers
current_followers = set(follower.username for follower in profile.get_followers())

if os.path.exists("previous_followers.json"):
    #load previous followers
    with open("previous_followers.json", "r") as f:
        previous_followers = set(json.load(f))

    unfollowers = previous_followers - current_followers

    if unfollowers:
        print("Users who have unfollowed you since the last check:")
        for user in unfollowers:
            print(user)
    else:
        print("No users have unfollowed you since the last check.")

    new_followers = current_followers - previous_followers

    if new_followers:
        print("\nNew followers since the last check:")
        for user in new_followers:
            print(user)

else:
    print("No previous follower data found. Creating new record.")

with open("previous_followers.json", "w") as f:
    json.dump(list(current_followers), f)

print("Follower data has been updated.")
