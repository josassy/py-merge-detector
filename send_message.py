import sys
from slackbot import post_message

if (len(sys.argv) > 1):
  response = post_message(sys.argv[1])
  print(response.status_code, response.text)