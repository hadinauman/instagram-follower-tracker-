# Instagram Follower Tracker

Tracks your Instagram followers over time and notifies you when someone unfollows you or starts following you.

## Features
- Track followers and unfollowers over time
- Timestamps for each check
- Session management (no need to login every time)
- Automatic retry with rate limit handling
- Progress bar while fetching followers
- Command line arguments for easy use

## Requirements
- Python 3.x
- `pip install instaloader tqdm`

### Basic usage:
```bash
python follower-tracker.py
```
Enter your username when prompted, login, and the script will track changes.

### With command line arguments:
```bash
python follower-tracker.py your_username
```

### Force new login (ignore saved session):
```bash
python follower-tracker.py your_username --login
```

## How it works
1. Logs you in and saves your current followers list
2. Subsequent runs compare against the previous data
3. Shows who unfollowed and who started following since last check
4. Saves timestamp of each check

## Important Notes
- **Rate limits**: Instagram limits automated requests. Don't run too frequently (once per day recommended)
- **First run**: Only saves base data, comparison starts on second run
- **Private data**: Works for private accounts and all data is stored locally

## Known Issues
- May hit Instagram rate limits if run too frequently
- Fetching followers can take several minutes for large follower counts
