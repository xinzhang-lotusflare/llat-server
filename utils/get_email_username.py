import sys

if len(sys.argv) < 2:
  print("Need user's email address")
  sys.exit(1)
user_email_addr = sys.argv[1]
new_name = user_email_addr.partition("@")[0]
print(new_name)
