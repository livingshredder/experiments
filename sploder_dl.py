import argparse
import requests

parser = argparse.ArgumentParser(description='Downloads levels from Sploder for archival purposes.')
parser.add_argument('-u', '--username', action='store', required=True)
parser.add_argument('-p', '--password', action='store', required=True)

args = parser.parse_args()

session = requests.Session()
result = session.post('https://www.sploder.com/accounts/login/login_handler.php', {
    'username': args.username,
    'password': args.password
})

result.raise_for_status()

