import requests


# Step 1: Authenticate and retrieve the access token
def get_access_token():
    auth_url = "https://nepalstock.com/api/authenticate/prove"

    # Headers for the authentication request
    auth_headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "dnt": "1",
        "priority": "u=1, i",
        "referer": "https://nepalstock.com/today-price",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    try:
        # Send the request to authenticate with SSL verification disabled
        response = requests.get(auth_url, headers=auth_headers, verify=False)

        if response.status_code == 200:
            auth_data = response.json()
            print(auth_data)
            access_token = auth_data.get("accessToken")

            if access_token:
                print("Access token retrieved successfully.")
                return access_token
            else:
                print("Failed to retrieve access token.")
                return None
        else:
            print(f"Authentication failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None


# Step 2: Fetch data from the API using the retrieved access token
def fetch_today_price_data(access_token):
    api_url = "https://nepalstock.com/api/nots/nepse-data/today-price"

    # Headers for the data request
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Salter {access_token}",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://nepalstock.com",
        "referer": "https://nepalstock.com/today-price",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    # Example payload (adjust as needed)
    payload = {"id": 525998}  # Replace with appropriate ID logic if required

    try:
        # Send the POST request to fetch data with SSL verification disabled
        response = requests.post(api_url, headers=headers, json=payload, verify=False)


        if response.status_code == 200:
            print("Data fetched successfully:")
            print(response.text)
            return response.json()
        else:
            print(f"Failed to fetch data with status code: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error during data fetching: {e}")
        return None


# Main program execution
if __name__ == "__main__":
    # Step 1: Authenticate and get the access token
    token = get_access_token()

    if token:
        # Step 2: Fetch today's price data using the access token
        data = fetch_today_price_data(token)

        if data:
            print(data)  # Print or process the fetched data
