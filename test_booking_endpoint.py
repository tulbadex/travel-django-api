import requests
import json

# Test the booking endpoint
url = "http://localhost:8000/api/flights/bookings/"

# Test data
data = {
    "flight_id": 1912,
    "passenger_count": 2,
    "travel_class": "economy",
    "passengers": [
        {
            "first_name": "ibrahim",
            "last_name": "adedayo",
            "email": "tulbadex@gmail.com",
            "phone": "09051612345"
        },
        {
            "first_name": "Rasheed",
            "last_name": "Adedayo", 
            "email": "rasheedadedayo@gmail.com",
            "phone": "09056721345"
        }
    ]
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Token your_token_here'  # Replace with actual token
}

try:
    # Test GET request
    print("Testing GET request...")
    response = requests.get(url)
    print(f"GET Status: {response.status_code}")
    print(f"GET Response: {response.text[:200]}...")
    
    # Test POST request
    print("\nTesting POST request...")
    response = requests.post(url, json=data, headers=headers)
    print(f"POST Status: {response.status_code}")
    print(f"POST Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")