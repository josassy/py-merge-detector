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
    time.sleep(60*15)

def checkout(repo_name: str, branch_name: str):
  repo = Repo(repo_name)
  repo.git.fetch()
  print(repo.git.checkout(branch_name))

def update(repo_name: str, branch_name: str):
  repo = Repo(repo_name)
  # loop infinitely until the fetch works
  while True:
    try:
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
    message = get_message(commit.author.name, pr_name, branch_name)
    print(message)
    post_message(message)

    if not path.exists(RECORD_NAME):
      with open (RECORD_NAME, 'w') as record_file:
        record_file.write('{}')
    
    read_and_update_record(commit.author.name)

def read_and_update_record(author_name: str):
  if path.exists(RECORD_NAME):
    dev_record = {}
    with open(RECORD_NAME, 'r') as json_file:
      dev_record = json.load(json_file)

      if author_name in dev_record:
        last_date = dt.strptime(dev_record[author_name], '%m/%d/%Y').date()
        today = date.today()
        days_difference = (today - last_date).days
        post_message(get_date_message(author_name.split(' ')[0], days_difference))

      dev_record[author_name] = date.today().strftime('%m/%d/%Y')
    
    with open(RECORD_NAME, 'w') as json_file:
      json_file.write(json.dumps(dev_record))

def get_message(author_name: str, pr_name: str, branch_name: str) -> str:
  first_name = author_name.split(' ')[0]
  weekday = dt.today().strftime("%A")
  messages = [
    f"Looks like {author_name} has finally merged {pr_name} to {branch_name}. Good job, {first_name}. :clap:",
    f"{author_name} just checked in {pr_name} to {branch_name}. At least {first_name} is getting work done. :computer:",
    f"Congratulations to {author_name} for merging {pr_name} to {branch_name}! :tada:",
    f"Just noticed that {author_name} just pushed {pr_name} to {branch_name}. Excellent... :fire:",
    f"You won't believe this, but {author_name} actually merged some code to {branch_name} just now. Somehow their PR {pr_name} was approved. :see_no_evil:",
    f"Oh look, {author_name} just merged {pr_name} to {branch_name}. How about that. :eyes:",
    f"Don't look now, but {branch_name} just got updated with {author_name}'s PR {pr_name}. Glad we are paying {first_name} for something. :money_with_wings:",
    f"{pr_name} just got merged to {branch_name}. Hopefully {author_name} didn't break anything this time. :exploding_head:",
    f"Big kudos to {author_name} for merging {pr_name} to {branch_name}. It's great to see {first_name} building their dreams, one commit at a time. :mountain:",
    f"Let's all give a big round of applause to {author_name} for merging {pr_name} to {branch_name}. Excellent work, {first_name}. :raised_hands:",
    f"{author_name} just merged {pr_name} to {branch_name}. Nice work, {first_name}. :partying_face:",
    f"Just received another hot merge to {branch_name}, courtesy of {author_name} ({pr_name}). Excellent... :sunglasses:",
    f"Another {weekday}, another merge to {branch_name}. We are all indebted to {author_name} for their excellent work on {pr_name} :pinched_fingers:",
    f"It's {weekday}, my dudes. It's also time to recognize {author_name} for their newly-merged work on {pr_name}. :v:",
    f"Haters will say that I'm getting \"spicy\", but I'm really just here to congratulate {author_name} for merging {pr_name} to {branch_name}. Good job, I guess. :shrug:",
    f"I want you all to know that {author_name} is actually getting work done today, unlike the rest of you. They just merged {pr_name} to {branch_name}. Now if everyone else would quit slacking off... :upside_down_face:",
    f"Against all odds, {author_name} got their PR {pr_name} approved and merged to {branch_name}. This should be remembered as a feat of awesomeness. :muscle:",
    f"In classic form, {author_name} merged yet again to {branch_name}. I'm so blown away I can't even tell you what it was. :zany_face:",
    f"Shout out to {first_name} for finishing a thing today. :+1:",
    f"It's {weekday}, and something was just merged. I'm too tired to tell you what it was. :sleeping:",
    f"I see you, {first_name} :eyes:",
    f"\"_mErGe bOt iS gEtTiNg sPiCy_\" :face_with_rolling_eyes: (gg {first_name} for finally merging {pr_name})",
    f"I need a vacation. So does {first_name} after their latest PR. :palm_tree:",
    f"{pr_name} just got merged to {branch_name}. I won't tell you who did it. :see_no_evil:",
    f"{pr_name} just got merged to {branch_name}. Everyone say, gogo {first_name}! :rocket:",
    f"Friendly reminder that {first_name} is the real MVP around here. :star:",
    f":newspaper: _This just in:_ \"Local software engineer {author_name} actually gets something done today, having merged {pr_name} to {branch_name}\""
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


