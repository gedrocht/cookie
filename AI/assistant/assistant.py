import gmail
import gpt
import tts

from time import sleep

def print_email(email):
  print(email)

def main():
  gmail_service, emails = gmail.init()

  while True:
    emails, new_emails = gmail.get_new_emails(gmail_service, emails)
    if len(new_emails) > 0:
      print("===================")
      for email in new_emails:
        print(email)
        summary = gpt.get_chatgpt_response(str(email))
        print_email(email)
        print("--------------------------------")
        print(summary)
        print('================================')
        tts.speak(summary)
    sleep(30)

if __name__ == "__main__":
  main()
