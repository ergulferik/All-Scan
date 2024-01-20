import requests


class DatabaseUpdater:
    def __init__(self, base_url):
        self.base_url = base_url

    def drop_database(self, username, password):
        api_url = f"{self.base_url}/drop-database"
        admin_data = {'userName': username, 'password': password}
        response = requests.get(api_url, json=admin_data)

        if response.status_code == 200:
            print("Successful:", response.text)
        else:
            print("Failed:", response.text)

    def update_database(self, username, password):
        api_url = f"{self.base_url}/update-database"
        admin_data = {'userName': username, 'password': password}
        response = requests.get(api_url, json=admin_data)

        if response.status_code == 200:
            print("Successful:", response.text)
        else:
            print("Failed:", response.text)


def main():
    base_url = 'http://127.0.0.1:8000'
    updater = DatabaseUpdater(base_url)

    while True:
        process = input("What operation would you like to perform?\n 1-Update Database \n 2-Drop Database\n")

        if process == '1' or process.lower() == 'update' or process.lower() == 'update database':
            print("Please enter your username and password:")
            username = input("Username: ")
            password = input("Password: ")
            updater.update_database(username, password)

        elif process == '2' or process.lower() == 'drop' or process.lower() == 'drop database':
            print("Please enter your username and password:")
            username = input("Username: ")
            password = input("Password: ")
            updater.drop_database(username, password)


if __name__ == "__main__":
    main()
