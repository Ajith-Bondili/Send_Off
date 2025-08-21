#!/usr/bin/env python3
import datetime
import subprocess
import random

# REALISTIC pattern: Sometimes 3 days/week, sometimes 1 day, sometimes 6 days
# Natural gaps, irregular patterns, totaling ~250 commits March 1 - July 11
commit_schedule = {
    # March - Week 1: 3 days active
    "2025-03-03": 4,  # Monday
    "2025-03-05": 2,  # Wednesday  
    "2025-03-07": 3,  # Friday
    
    # March - Week 2: 1 day only (busy elsewhere)
    "2025-03-11": 7,  # Tuesday only
    
    # March - Week 3: 6 days active (big sprint)
    "2025-03-17": 3,  # Monday
    "2025-03-18": 5,  # Tuesday
    "2025-03-19": 4,  # Wednesday
    "2025-03-20": 6,  # Thursday
    "2025-03-21": 2,  # Friday
    "2025-03-22": 1,  # Saturday
    
    # March - Week 4: 2 days
    "2025-03-25": 5,  # Tuesday
    "2025-03-28": 3,  # Friday
    
    # April - Week 1: 4 days
    "2025-04-01": 2,  # Tuesday
    "2025-04-02": 6,  # Wednesday
    "2025-04-04": 4,  # Friday
    "2025-04-05": 1,  # Saturday
    
    # April - Week 2: 1 day only
    "2025-04-09": 8,  # Wednesday
    
    # April - Week 3: 5 days (another sprint)
    "2025-04-14": 3,  # Monday
    "2025-04-15": 7,  # Tuesday
    "2025-04-16": 4,  # Wednesday
    "2025-04-17": 5,  # Thursday
    "2025-04-19": 2,  # Saturday
    
    # April - Week 4: 2 days
    "2025-04-22": 6,  # Tuesday
    "2025-04-25": 3,  # Friday
    
    # May - Week 1: 3 days
    "2025-05-01": 1,  # Thursday
    "2025-05-02": 5,  # Friday
    "2025-05-03": 2,  # Saturday
    
    # May - Week 2: 6 days (busy week)
    "2025-05-05": 4,  # Monday
    "2025-05-06": 6,  # Tuesday
    "2025-05-07": 3,  # Wednesday
    "2025-05-08": 7,  # Thursday
    "2025-05-09": 2,  # Friday
    "2025-05-10": 1,  # Saturday
    
    # May - Week 3: 1 day only
    "2025-05-14": 9,  # Wednesday
    
    # May - Week 4: 4 days
    "2025-05-19": 3,  # Monday
    "2025-05-21": 5,  # Wednesday
    "2025-05-22": 4,  # Thursday
    "2025-05-24": 2,  # Saturday
    
    # May - Week 5: 2 days
    "2025-05-27": 6,  # Tuesday
    "2025-05-30": 3,  # Friday
    
    # June - Week 1: 5 days
    "2025-06-02": 2,  # Monday
    "2025-06-03": 4,  # Tuesday
    "2025-06-04": 7,  # Wednesday
    "2025-06-05": 3,  # Thursday
    "2025-06-07": 1,  # Saturday
    
    # June - Week 2: 3 days
    "2025-06-10": 5,  # Tuesday
    "2025-06-12": 8,  # Thursday
    "2025-06-13": 2,  # Friday
    
    # June - Week 3: 1 day only
    "2025-06-18": 6,  # Wednesday
    
    # June - Week 4: 4 days
    "2025-06-23": 3,  # Monday
    "2025-06-24": 4,  # Tuesday
    "2025-06-26": 5,  # Thursday
    "2025-06-28": 1,  # Saturday
    
    # July - Week 1: 2 days
    "2025-07-01": 4,  # Tuesday
    "2025-07-03": 2,  # Thursday
    
    # July - Week 2: 3 days (final week)
    "2025-07-07": 3,  # Monday
    "2025-07-09": 5,  # Wednesday
    "2025-07-11": 2,  # Friday
}

def create_commits_for_date(date_str, count):
    """Create commits spread throughout the day"""
    if count == 0:
        return
    
    base_hour = random.randint(9, 12)  # Start between 9 AM - 12 PM
    
    for i in range(count):
        # Spread commits throughout the day (1-3 hours apart)
        hour_gap = random.randint(1, 3)
        hour = min(23, base_hour + (i * hour_gap))
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        timestamp = f"{date_str} {hour:02d}:{minute:02d}:{second:02d}"
        
        # Write to commit_bot.txt
        with open("commit_bot.txt", "w") as f:
            f.write(f"{timestamp} - Update {i+1}/{count}")
        
        subprocess.run(["git", "add", "commit_bot.txt"], check=True)
        subprocess.run([
            "git", "commit", 
            "-m", "Update commit_bot.txt",
            "--date", timestamp
        ], check=True)

# Execute the realistic schedule
total_commits = 0
active_days = 0
for date_str, count in sorted(commit_schedule.items()):
    create_commits_for_date(date_str, count)
    total_commits += count
    active_days += 1
    print(f"{date_str}: {count} commits")

print(f"\n✅ Generated {total_commits} commits across {active_days} active days!")
print("Pattern: Sometimes 1 day/week, sometimes 3 days, sometimes 6 days")
