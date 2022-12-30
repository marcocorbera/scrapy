# Python dependencies
import pathlib
import datetime
from os import close, path
import os
import requests
import lxml.html as html
import json

# Constants created in another file
from constants import HOME_URL, XPATH_BITCOIN_PAGE, XPATH_NODES, VALUES_LIST, SAVED_JSON, TEMPORARY_JSON


# Menu to select an option
def menu():
    """Program menu"""
    print(f"""
########## Welcome to the bitcoin scraper!##########

Please, select an option

1) Get data from {HOME_URL}
2) Show the saved scraped data (if it exists)
3) Exit
"""
          )

    # Validating option
    while True:
        option = input('Select a valid option: ')
        try:
            option = int(option)
            if (option == 1 or option == 2 or option == 3):
                return option
            elif (option != 1 and option != 2 and option != 3):
                continue
        except ValueError:
            print('Wrong input!')


# Prints the saved data
def print_data():
    """Function to print the saved Bitcoin data"""
    actual_dir = os.listdir(pathlib.Path.cwd())
    if SAVED_JSON in actual_dir:
        with open(SAVED_JSON, 'r') as f:
            data_to_print = json.load(f)
            print(f'Saved data: \n {json.dumps(data_to_print, indent=4)}')
    else:
        print('There is no data saved yet!')


# Function to convert from list to string
def convert_array(array):
    return ''.join(array)


# Prints data obtained with format json
def print_json(data):
    print(f'Data obtained: {json.dumps(data, indent=4)}')


def save_data(data, time):
    """"Overwrite json if exists or create it"""
    actual_dir = os.listdir(pathlib.Path.cwd())

    # Gets the actual json if it exists, then write the old data with the new data
    # In another file, delete the older and rename the new, so it "overwrite"
    # the original file
    if SAVED_JSON in actual_dir:
        with open(SAVED_JSON, 'r') as f:

            saved_data = json.load(f)
            f.close()

            data_to_save = saved_data
            data_to_save['values'].append({f'{time}': data})

            with open(TEMPORARY_JSON, 'w') as file:
                json.dump(data_to_save, file, indent=4)
                file.close()

                os.remove(SAVED_JSON)
                os.rename(TEMPORARY_JSON, SAVED_JSON)

    else:
        with open(SAVED_JSON, 'w') as f:
            data_to_save = {}
            data_to_save['asset'] = 'BTC'
            data_to_save['values'] = []
            data_to_save['values'].append({f'{time}': data})
            json.dump(data_to_save, f, indent=4)
            f.close()


# Obtaining every value from bitcoing page
def parse_bitcoin(link):
    """Scraping the requested data"""
    response = requests.get(link)
    try:
        if response.status_code == 200:
            bitcoin_page = response.content.decode('utf-8')
            parsed = html.fromstring(bitcoin_page)
            data = dict()
            data['Obtained'] = datetime.datetime.now().strftime(
                'Day: %d-%m-%Y Hour: %H:%M:%S')
            # Using Values list to create every value in the dictionary
            for index, value in enumerate(VALUES_LIST):
                # Converting from lists to string every text found and
                # inserting them into the dict
                text_from_html_array = parsed.xpath(XPATH_NODES[index])
                # text_from_html_array returns mobile and desktop values
                # it's needed to select the first one
                if value == 'Market Dominance' or value == 'Price Change':
                    data[value] = convert_array(text_from_html_array[0: 2])
                else:
                    data[value] = convert_array(text_from_html_array[0])
            # Saving the time this  data was obtained
            data['Obtained'] = datetime.datetime.now().strftime(
                'Day: %d-%m-%Y Hour: %H:%M:%S')
            return data
        else:
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)


def parse_home():
    """Function to obtain Bitcoin page link"""
    response = requests.get(HOME_URL)
    try:
        if response.status_code == 200:
            home = response.content.decode('utf-8')
            parsed = html.fromstring(home)
            link = convert_array(parsed.xpath(XPATH_BITCOIN_PAGE))
            # Adding the bitcoin path to the home url
            bitcoin_link = HOME_URL + link
            return bitcoin_link
        else:
            raise ValueError(f'Error: {response.status_code}')
    except ValueError as ve:
        print(ve)


def run():
    """Controls the flow of the program"""
    option = menu()
    if option == 1:
        link_to_bitcoin_page = parse_home()
        data = parse_bitcoin(link_to_bitcoin_page)
        print_json(data)
        time = data['Obtained']
        save_data(data, time)
    elif option == 2:
        print_data()
    print('Thanks for using this program, come back later!')


if __name__ == '__main__':
    run()
