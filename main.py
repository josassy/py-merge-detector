from git import Repo
import time
import sys
from settings import REPO_NAME
from slackbot import post_message


def main(branch_name: str = "develop"):
  done = False

  checkout(branch_name)

  while not done:
    update(branch_name)
    time.sleep(60*5)

def checkout(branch_name: str):
  repo = Repo(REPO_NAME)
  repo.git.fetch()
  print(repo.git.checkout(branch_name))

def update(branch_name: str):
  repo = Repo(REPO_NAME)
  output = repo.git.pull()
  if not 'Already up to date.' in output:
    print("updated!")
    commit = repo.commit('HEAD')
    pr_name = commit.message.split('\n')[0]
    print(output)
    message = f'🎉 Congratulations to {commit.author} for merging {pr_name} to develop! 🎉' 
    print(message)
    post_message(message)
if __name__ == "__main__":
  if (len(sys.argv) > 1):
    main(sys.argv[1])
  else:
    main()

