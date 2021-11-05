from git import Repo
import time
import sys
from settings import DEFAULT_REPO, RECORD_NAME, DEFAULT_BRANCH
from slackbot import post_message
from os import path
from datetime import date, datetime as dt
import json
import math
import random
from datetime import datetime as dt

def main():
  repo = DEFAULT_REPO
  branch_name = DEFAULT_BRANCH
  done = False

  print("""\
___  ___                     ______       _   
|  \/  |                     | ___ \     | |  
| .  . | ___ _ __ __ _  ___  | |_/ / ___ | |_ 
| |\/| |/ _ \ '__/ _` |/ _ \ | ___ \/ _ \| __|
| |  | |  __/ | | (_| |  __/ | |_/ / (_) | |_ 
\_|  |_/\___|_|  \__, |\___| \____/ \___/ \__|
                  __/ |                       
                 |___/                        
""")  
  print("Welcome to Merge Bot.")
  user_input = input(f"Repo to monitor: (default: {repo})")
  if (user_input):
    repo = user_input
  user_input = input(f"Branch to watch: (default: {branch_name})")
  if (user_input):
    branch_name = user_input

  checkout(repo, branch_name)

  while not done:
    update(repo, branch_name)
    time.sleep(60*5)

def checkout(repo_name: str, branch_name: str):
  repo = Repo(repo_name)
  repo.git.fetch()
  print(repo.git.checkout(branch_name))

def update(repo_name: str, branch_name: str):
  repo = Repo(repo_name)
  # loop infinitely until the fetch works
  while True:
    try:
      print(f'pulling {dt.now()}')
      output = repo.git.pull()
      # if completes with no errors, break out of loop
      break
    except Exception as e:
      print(f'exception at {dt.now()}:\n{e}')
      print('waiting 5 minutes...')
      time.sleep(60*5)
  if not 'Already up to date.' in output:
    print(f"updated! ({dt.now()})")
    commit = repo.commit('HEAD')
    pr_name = commit.message.split('\n')[0]
    print(pr_name)
    message, quiet = get_message(commit.author.name, pr_name, branch_name)
    print(message)
    post_message(message)

    if not path.exists(RECORD_NAME):
      with open (RECORD_NAME, 'w') as record_file:
        record_file.write('{}')
    
    read_and_update_record(commit.author.name, quiet)


def read_and_update_record(author_name: str, quiet: bool = False):
  if path.exists(RECORD_NAME):
    dev_record = {}
    with open(RECORD_NAME, 'r') as json_file:
      dev_record = json.load(json_file)

      # if quiet flag was set, don't post a message
      if author_name in dev_record and not quiet:
        last_date = dt.strptime(dev_record[author_name], '%m/%d/%Y').date()
        today = date.today()
        days_difference = (today - last_date).days
        post_message(get_date_message(author_name.split(' ')[0], days_difference))

      dev_record[author_name] = date.today().strftime('%m/%d/%Y')
    
    with open(RECORD_NAME, 'w') as json_file:
      json_file.write(json.dumps(dev_record))

# returns the string message, and boolean indicating whether or not the message is anonymous
def get_message(author_name: str, pr_name: str, branch_name: str) -> tuple:
  first_name = author_name.split(' ')[0]
  weekday = dt.today().strftime("%A")
  messages = [
    (f"Looks like {author_name} has finally merged {pr_name} to {branch_name}. Good job, {first_name}. :clap:", False),
    (f"{author_name} just checked in {pr_name} to {branch_name}. At least {first_name} is getting work done. :computer:", False),
    (f"Congratulations to {author_name} for merging {pr_name} to {branch_name}! :tada:", False),
    (f"Just noticed that {author_name} just pushed {pr_name} to {branch_name}. Excellent... :fire:", False),
    (f"You won't believe this, but {author_name} actually merged some code to {branch_name} just now. Somehow their PR {pr_name} was approved. :see_no_evil:", False),
    (f"Oh look, {author_name} just merged {pr_name} to {branch_name}. How about that. :eyes:", False),
    (f"Don't look now, but {branch_name} just got updated with {author_name}'s PR {pr_name}. Glad we are paying {first_name} for something. :money_with_wings:", False),
    (f"{pr_name} just got merged to {branch_name}. Hopefully {author_name} didn't break anything this time. :exploding_head:", False),
    (f"Big kudos to {author_name} for merging {pr_name} to {branch_name}. It's great to see {first_name} building their dreams, one commit at a time. :mountain:", False),
    (f"Let's all give a big round of applause to {author_name} for merging {pr_name} to {branch_name}. Excellent work, {first_name}. :raised_hands:", False),
    (f"{author_name} just merged {pr_name} to {branch_name}. Nice work, {first_name}. :partying_face:", False),
    (f"Just received another hot merge to {branch_name}, courtesy of {author_name} ({pr_name}). Excellent... :sunglasses:", False),
    (f"Another {weekday}, another merge to {branch_name}. We are all indebted to {author_name} for their excellent work on {pr_name} :pinched_fingers:", False),
    (f"It's {weekday}, my dudes. It's also time to recognize {author_name} for their newly-merged work on {pr_name}. :v:", False),
    (f"Haters will say that I'm getting \"spicy\", but I'm really just here to congratulate {author_name} for merging {pr_name} to {branch_name}. Good job, I guess. :shrug:", False),
    (f"I want you all to know that {author_name} is actually getting work done today, unlike the rest of you. They just merged {pr_name} to {branch_name}. Now if everyone else would quit slacking off... :upside_down_face:", False),
    (f"Against all odds, {author_name} got their PR {pr_name} approved and merged to {branch_name}. This should be remembered as a feat of awesomeness. :muscle:", False),
    (f"In classic form, {author_name} merged yet again to {branch_name}. I'm so blown away I can't even tell you what it was. :zany_face:", False),
    (f"Shout out to {first_name} for finishing a thing today. :+1:", False),
    (f"It's {weekday}, and something was just merged. I'm too tired to tell you what it was. :sleeping:", True),
    (f"I see you, {first_name} :eyes:", False),
    (f"\"_mErGe bOt iS gEtTiNg sPiCy_\" :face_with_rolling_eyes: (gg {first_name} for finally merging {pr_name})", False),
    (f"I need a vacation. So does {first_name} after their latest PR. :palm_tree:", False),
    (f"{pr_name} just got merged to {branch_name}. I won't tell you who did it. :see_no_evil:", True),
    (f"{pr_name} just got merged to {branch_name}. Everyone say, gogo {first_name}! :rocket:", False),
    (f"Friendly reminder that {first_name} is the real MVP around here. :star:", False),
    (f":newspaper: _This just in:_ \"Local software engineer {author_name} actually gets something done today, having merged {pr_name} to {branch_name}\"", False),
    (f"{branch_name} is likely in shambles after someone merged {pr_name}. 👀", True),
    (f"Today is clearly another good day for {first_name} after they successfully merged {pr_name}. Nice work.", False),
    (f"I certainly hope that {first_name} feels appreciated for their fantastic work on {pr_name}. It just hit {branch_name} with such speed that no one saw it coming.", False),
    (f"Everyone type 'git fetch --all && git merge origin/{branch_name}' because {author_name} just merged {pr_name}. What exciting times we live in.", False),
    (f"Roses are red, violets are blue, {first_name} is amazing, and you could be, too", False),
    (f"Just spilled coffee all over my keyboard upon learning that {first_name} actuall managed to merge {pr_name} to {branch_name}. I don't even know how I am typing this.", False),
    (f"{first_name} just merged {pr_name}. I'm on the edge of my seat waiting to hear what they will do next.", False),
    (f"\"Already up to date.\" is NOT what you would read after pulling {branch_name}, (you should try it)", True),
    (f"{pr_name} just got  M E R G E D :tada::tada::tada::tada::tada::tada:", True),
    (f":eyes:", True)
  ]
  return messages[math.floor(random.random() * len(messages))]

def get_date_message(name: str, num_days: int) -> str:
  if num_days == 0:
    return f'{name} has merged to develop multiple times today.'
  elif num_days == 1:
    return f'{name} merged to develop yesterday, too.'
  elif num_days <= 30:
    return f'{name} last merged with develop {num_days} days ago.'
  else:
    return f"This is the first time {name} has merged with develop in over a month ({num_days} days)."


if __name__ == "__main__":
  main()


