from git import Repo
import time
import sys
from settings import REPO_NAME, RECORD_NAME
from slackbot import post_message
from os import path
from datetime import date, datetime as dt
import json
import math
import random

def main(branch_name: str = "develop"):
  done = False

  checkout(branch_name)

  while not done:
    update(branch_name)
    time.sleep(60*15)

def checkout(branch_name: str):
  repo = Repo(REPO_NAME)
  repo.git.fetch()
  print(repo.git.checkout(branch_name))

def update(branch_name: str):
  repo = Repo(REPO_NAME)
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
  messages = [
    f"Looks like {author_name} has finally merged {pr_name} to {branch_name}. Good job, {first_name}. :clap:",
    f"{author_name} just checked in {pr_name} to {branch_name}. At least {first_name} is getting work done. :computer:",
    f"Congratulations to {author_name} for merging {pr_name} to {branch_name}! :tada:",
    f"Just noticed that {author_name} just pushed {pr_name} to {branch_name}. One step closer to world domination. :fire:",
    f"You won't believe this, but {author_name} actually merged some code to {branch_name} just now. Somehow their PR {pr_name} was approved. :see_no_evil:",
    f"Oh look, {author_name} just merged {pr_name} to {branch_name}. How about that. :eyes:",
    f"Don't look now, but {branch_name} just got updated with {author_name}'s PR {pr_name}. Glad we are paying {first_name} for something. :money_with_wings:",
    f"{pr_name} just got merged to {branch_name}. Hopefully {author_name} didn't break anything this time. :exploding_head:",
    f"Big kudos to {author_name} for merging {pr_name} to {branch_name}. It's great to see {first_name} building their dreams, one commit at a time. :mountain:",
    f"I've noticed that {author_name} had the audacity to merge {pr_name} to {branch_name}. Who does {first_name} think they are, anyway? A software developer? :thinking_face:",
    f"Let's all give a big round of applause to {author_name} for merging {pr_name} to {branch_name}. Excellent work, {first_name}. :raised_hands:"
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
  if (len(sys.argv) > 1):
    main(sys.argv[1])
  else:
    main()


