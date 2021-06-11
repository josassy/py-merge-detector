from git import Repo
import time
import sys

def main(branch_name: str = "develop"):
  done = False

  while not done:
    update(branch_name)
    time.sleep(10)

def update(branch_name: str):
  repo = Repo('C:/Users/jlansford/source/repos/max_shadow')
  print(repo.git.checkout(branch_name))
  output = repo.git.pull()
  if not output == 'Already up to date.':
    print("updated!")
  else:
    print("no update")

if __name__ == "__main__":
  if (len(sys.argv) > 1):
    main(sys.argv[1])
  else:
    main()

