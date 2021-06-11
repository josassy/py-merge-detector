from slackbot import post_message

response = post_message("Hello, World! 🎉")
print(response.status_code, response.text)