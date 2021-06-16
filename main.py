from git import Repo
import time
import sys
from settings import REPO_NAME, RECORD_NAME
from slackbot import post_message
from os import path
from datetime import date, datetime as dt
import json

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
  output = repo.git.pull()
  if not 'Already up to date.' in output:
    print(f"updated! ({dt.now()}")
    commit = repo.commit('HEAD')
    pr_name = commit.message.split('\n')[0]
    print(pr_name)
    message = get_message(commit.author.name, pr_name)
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

def get_message(author_name: str, pr_name: str) -> str:
  if author_name == "Mark Brown":
    return f':flag-ca: :flag-ca: :flag-ca: :flag-ca: Congratulations to ${author_name} for merging ${pr_name} into develop! :flag-ca: :flag-ca: :flag-ca: :flag-ca:'
  elif author_name == "Brian Hughes":
    return f'Notice: :qt: QML SME ${author_name} has merged ${pr_name} into develop'
  elif author_name == "Daschel Fortner":
    return f":bologna: SME ${author_name} has merged ${pr_name}. It's probably mostly :bologna:."
  elif author_name == "Josiah Lansford":
    return f":${author_name} just merged ${pr_name} into develop. Consider reverting immediately. :bread:"
  else:
    return f'🎉 Congratulations to {author_name} for merging {pr_name} to develop! 🎉'

def get_date_message(name: str, num_days: int) -> str:
  if num_days == 0:
    return f'{name} has merged to develop multiple times today. {name} is on fire! 🔥'
  elif num_days == 1:
    return f'{name} merged to develop yesterday, too. {name} is on a roll!'
  elif num_days <= 7:
    return f'{name} last merged to develop only {num_days} days ago. What a MVP.'
  elif num_days <= 14:
    return f"{name} last merged with develop {num_days} days ago. What consistent style and grace."
  elif num_days <= 30:
    return f'{name} last merged with develop {num_days} days ago. Glad to see {name} is still a contributor.'
  else:
    return f"This is the first time {name} has merged with develop in over a month ({num_days} days). Give {name} a hearty congratulations."


if __name__ == "__main__":
  if (len(sys.argv) > 1):
    main(sys.argv[1])
  else:
    main()


