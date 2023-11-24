from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import subprocess
import os
import re

print("""
   ______            __             __  __  __                           __     ____           
  / ____/___  ____  / /_____ ______/ /_/ / / /___ _______   _____  _____/ /_   / __ \_________ 
 / /   / __ \/ __ \/ __/ __ `/ ___/ __/ /_/ / __ `/ ___/ | / / _ \/ ___/ __/  / /_/ / ___/ __ \\
/ /___/ /_/ / / / / /_/ /_/ / /__/ /_/ __  / /_/ / /   | |/ /  __(__  ) /_   / ____/ /  / /_/ /
\____/\____/_/ /_/\__/\__,_/\___/\__/_/ /_/\__,_/_/    |___/\___/____/\__/  /_/   /_/   \____/ 
                                                                                               
    Inspired from the work of gathercontacts burp extension (Credit: m4xx101, FR13ND0x7F) \n""")


def gather_contacts(company):
    browser = webdriver.Chrome()
    browser.get('https://www.google.com')
    time.sleep(1)

    search_box = browser.find_element(By.NAME, 'q')
    search_box.send_keys(f'site:linkedin.com/in/ {company}')
    search_box.submit()

    print("Please scroll through all the results manually, then press Enter when done.")
    input()

    results = browser.find_elements(By.CSS_SELECTOR, "h3")
    names_with_designation = []

    for result in results:
        data = result.text.split('-')
        if len(data) > 1 and company.lower() in data[-1].lower():
            full_name_and_designation = data[0].strip()
            names_with_designation.append(full_name_and_designation)

    browser.close()
    return names_with_designation

def create_emails(names_with_designation, domain_name, format_option):
    emails = []

    format_options = {
        1: lambda first, last: f"{first[0]}{last}@{domain_name}",
        2: lambda first, last: f"{first}.{last}@{domain_name}",
        3: lambda first, last: f"{last}{first[0]}@{domain_name}",
        4: lambda first, last: f"{first}{last[0]}@{domain_name}",
    }

    for name_with_designation in names_with_designation:
        parts = name_with_designation.split()
        first_name = re.sub(r'[^a-zA-Z]', '', parts[0]).lower()
        last_name = re.sub(r'[^a-zA-Z]', '', parts[1]).lower() if len(parts) > 1 else ''

        emails.append(format_options[format_option](first_name, last_name))

    return emails

def get_linkedin_profiles(company_name):
    driver = webdriver.Chrome()

    try:
        driver.get("https://www.google.com/")
        search_box = driver.find_element("name", "q")
        search_box.send_keys(f"site:linkedin.com/in \"{company_name}\"")
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        titles_list = []

        while True:
            titles = driver.find_elements(By.XPATH, "//h3")

            for title in titles:
                titles_list.append(title.text)

            time.sleep(2)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        driver.quit()
        write_to_file(company_name, titles_list)

def write_to_file(company_name, titles_list):
    if titles_list:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{company_name}_{timestamp}.txt"

        try:
            with open(file_name, 'w') as file:
                for title in titles_list:
                    file.write(f"{title}\n")

            print(f"Data written to {file_name}")

            subprocess.run(f"sort {file_name} | uniq > sorted_{file_name}", shell=True)
            print(f"Data sorted and duplicates removed. Check 'sorted_{file_name}'.")

        except Exception as e:
            print(f"An error occurred while writing to the file: {str(e)}")

def main():
    print("Choose an option:")
    print("1. Gather LinkedIn profiles")
    print("2. Create emails and search LinkedIn profiles")

    option = int(input("Enter your choice (1 or 2): "))

    if option == 1:
        company_name = input("Enter the company name for Google dork query: ")
        get_linkedin_profiles(company_name)
    elif option == 2:
        company = input("Enter the company name for Google dork query: ")
        domain = input(f"Enter the domain (e.g. company.com) for {company}: ")
        output_directory = input("Enter the output directory (leave blank for the current directory): ") or "."

        names_with_designation = gather_contacts(company)

        print("\nSelect email format:")
        print("1. flastname@domain.com")
        print("2. firstname.lastname@domain.com")
        print("3. lastnamef@domain.com")
        print("4. firstnamel@domain.com")
        email_format = int(input("Enter choice (default is 1): ") or 1)

        emails = create_emails(names_with_designation, domain, email_format)

        date_time = time.strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(os.path.expanduser(output_directory), f"{domain}-{date_time}-emails.txt")

        with open(output_file, 'w') as f:
            f.write("\n".join(emails))

        names_file = os.path.join(os.path.expanduser(output_directory), f"{domain}-{date_time}-names.txt")

        with open(names_file, 'w') as f:
            f.write("\n".join(names_with_designation))

        print(f"\n{len(emails)} emails saved to: {output_file}")
        print(f"Names saved to: {names_file}")
        print(f"\nScript executed on {date_time}.")
        print("End of script execution.")
    else:
        print("Invalid option. Please choose 1 or 2.")

if __name__ == "__main__":
    main()
