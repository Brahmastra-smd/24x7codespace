import time
import os 
os.system('pip install requests')
os.system('clear')
import requests
import logging
from requests.exceptions import RequestException
from threading import Thread
from datetime import datetime

# Expiry date
expiry_date = datetime(2025, 10, 25)

def check_expiry():
    current_date = datetime.now()
    if current_date > expiry_date:
        print("THE FILE IS EXPIRED. DM TO BUY PAID FILE :- @botplays90")
        exit()

# Start a specific Codespace
def start_codespace(codespace_name, headers):
    try:
        logging.info(f"Starting Codespace: {codespace_name}...")
        start_url = f"https://api.github.com/user/codespaces/{codespace_name}/start"
        response = requests.post(start_url, headers=headers)
        response.raise_for_status()
        if response.status_code in (200, 202):
            logging.info(f"Codespace {codespace_name} is starting.")
            return True
    except RequestException as e:
        logging.error(f"Error starting Codespace {codespace_name}: {e}")
    return False

# Keep Codespace alive
def keep_alive(codespace_name, headers, interval=25):
    while True:
        try:
            logging.info(f"Keeping Codespace {codespace_name} alive...")
            url = f"https://api.github.com/user/codespaces/{codespace_name}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            state = response.json().get("state")
            logging.info(f"Codespace {codespace_name} state: {state}")
            if state == "Shutdown":
                logging.info(f"Codespace {codespace_name} is shut down. Restarting...")
                start_codespace(codespace_name, headers)
            time.sleep(interval)
        except RequestException as e:
            logging.error(f"Error pinging Codespace API for {codespace_name}: {e}")

# Handle Codespaces for a specific token
def handle_codespaces_for_token(token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        response = requests.get("https://api.github.com/user/codespaces", headers=headers)
        response.raise_for_status()
        codespaces = response.json().get("codespaces", [])
        if not codespaces:
            logging.info("No Codespaces found for this token.")
            return

        threads = []
        for codespace in codespaces:
            codespace_name = codespace["name"]
            logging.info(f"Found Codespace: {codespace_name}")
            start_codespace(codespace_name, headers)
            thread = Thread(target=keep_alive, args=(codespace_name, headers))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    except RequestException as e:
        logging.error(f"Error retrieving Codespaces for token: {e}")

# Main function
def main():
    check_expiry()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    try:
        with open("tokens.txt", "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error("tokens.txt not found. Ensure the file exists and contains tokens.")
        return

    threads = []
    for token in tokens:
        thread = Thread(target=handle_codespaces_for_token, args=(token,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
    