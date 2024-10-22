import requests
from requests.auth import HTTPBasicAuth
import json
import getpass
import os

# Prompt the user for single Splunk instance or a file containing multiple instances
def get_splunk_instances():
    choice = input("Do you want to provide (1) a single Splunk instance or (2) a list of instances from a file? Enter 1 or 2: ")
    
    if choice == '1':
        # Get a single Splunk instance
        splunk_host = input("Enter the Splunk instance URL (e.g., https://splunk-instance:8089): ")
        return [splunk_host]
    
    elif choice == '2':
        # Get the file containing multiple Splunk instance URLs
        file_path = input("Enter the path to the file with Splunk instance URLs: ")
        
        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                # Read each line and return as a list
                return [line.strip() for line in file.readlines() if line.strip()]
        else:
            print(f"File '{file_path}' not found.")
            return []
    
    else:
        print("Invalid choice, please enter 1 or 2.")
        return []

# Prompt the user for credentials
def get_credentials():
    username = input("Enter your Splunk username: ")
    password = getpass.getpass("Enter your Splunk password: ")
    return username, password

# Function to get the list of installed apps for a given Splunk instance
def get_installed_apps(splunk_host, username, password):
    try:
        installed_apps_endpoint = f"{splunk_host}/services/apps/local"
        # Perform the API request
        response = requests.get(
            installed_apps_endpoint,
            auth=HTTPBasicAuth(username, password),
            verify=False  # Disable SSL verification, if needed
        )
        
        # Check if the response is successful
        if response.status_code == 200:
            apps = response.json().get('entry', [])
            return apps
        else:
            print(f"Error fetching apps from {splunk_host}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error occurred while fetching apps from {splunk_host}: {e}")
        return []

# Function to check for updates and get current/available version numbers
def get_apps_with_updates(apps):
    apps_with_updates = []
    for app in apps:
        app_name = app['name']
        app_content = app['content']
        current_version = app_content.get('version')  # Current installed version
        update = app_content.get('update')  # Contains the update information
        
        if update:  # Check if there's an update available
            latest_version = update.get('version', 'Unknown')  # Get the latest version if available
            apps_with_updates.append({
                'name': app_name,
                'current_version': current_version,
                'latest_version': latest_version
            })
    return apps_with_updates

# Main function to execute the process for multiple instances
def main():
    # Get the Splunk instances
    splunk_instances = get_splunk_instances()
    
    if not splunk_instances:
        print("No Splunk instances provided. Exiting.")
        return
    
    # Get user credentials
    username, password = get_credentials()
    
    # Iterate over each Splunk instance and check for updates
    for splunk_host in splunk_instances:
        print(f"\nChecking Splunk instance: {splunk_host}")
        
        apps = get_installed_apps(splunk_host, username, password)
        
        if not apps:
            print(f"No apps found or error occurred on {splunk_host}.")
            continue
        
        apps_with_updates = get_apps_with_updates(apps)
        
        if apps_with_updates:
            print(f"The following apps on {splunk_host} have updates available:")
            for app in apps_with_updates:
                print(f"- {app['name']}: Current Version: {app['current_version']}, Latest Version: {app['latest_version']}")
        else:
            print(f"No apps have updates available on {splunk_host}.")

if __name__ == "__main__":
    main()
