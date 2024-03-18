import urllib.parse
import requests
import os
import json
import re

def normalize_location(location):
    if not location:  # Check for empty input
        return None
    
    normalized_location = location.lower().strip()
    
    # Skip inputs with less than 4 letters
    if len(normalized_location) < 4:
        return None
    else:
        if ',' in normalized_location: # Manage cases like "Roma, Italia"
            normalized_location = normalized_location.split(',')[0]

        # Remove parentheses and text within parentheses like in "Roma (Italia)"
        normalized_location = re.sub(r'\([^)]*\)', '', normalized_location)

        normalized_location = normalized_location.strip()

        return normalized_location

def get_coordinates(location):
    json_file_path = 'geonames_data.json' # Create an empty json file for storing data

    print(location) # Check the running of the code while running "main.py"

    if os.path.exists(json_file_path): # If the file already exist open it
        with open(json_file_path, 'r') as json_file:
            json_data = json.load(json_file)
    else:
        json_data = {}

    with open('errori.json', 'r') as error_file: # Open the file where the errors will be stored
        errori_location = json.load(error_file)

    clean_location = normalize_location(location) # Call normalize_location
    
    if not clean_location:  # Check for invalid or empty location
        return None
    
    if clean_location in json_data: # Check if the location is already stored in the json file "geonames_data" 
        existing_data = json_data[clean_location]
        return existing_data
    elif clean_location in errori_location: # Check if the location is already stored in "errori"
        return False
    else:
        # Set your GeoNames username
        username = 'aldomorodigitale'

        # Define parameters for the call
        parametri = {'q': clean_location, 'maxRows': 10, 'username': username}

        # Encode parameters
        location_encode = urllib.parse.urlencode(parametri)

        # Construct GeoNames API URL
        url = 'http://api.geonames.org/searchJSON?' + location_encode

        try:
            # Send GET request
            resp = requests.get(url)
            resp.raise_for_status()  # Raise HTTPError for non-200 status codes
            
            # Parse JSON response
            data = resp.json()

            for item in data["geonames"]:
                if item['fcl'] in ('L', 'A', 'P', 'H'):  # Check the feature class
                    if item['fcl'] == 'H':
                        item['fcl'] = 'A'
                    result = item
                    break

            if result and clean_location != "null": # Create variables of the results 
                latitude = str(result['lat'])
                longitude = str(result['lng'])
                address_type = str(result['fcl'])
                countryCode = str(result.get('countryCode'))
                toponymName = str(result['toponymName'])

                json_data[clean_location] = [longitude, latitude, address_type, countryCode, toponymName]

                with open(json_file_path, 'w') as json_file: # Store results in "geonames_data"
                    json.dump(json_data, json_file, indent=4)

                return json_data[clean_location]

            else: 
                with open('errori.json', 'w') as error_file:
                    errori_location[clean_location] = ["1"]
                    json.dump(errori_location, error_file)
                print("------------------- " + location)
                return False
            
        except requests.exceptions.RequestException as e:
            print("Error occurred during API request:", e)
            return None
        except KeyError:
            print("Invalid or unexpected API response format.")
            return None

