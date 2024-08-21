from gettext import install
from urllib import request


pip install Flask request # type: ignore
from flask import Flask, json5,request
import requests
import time
from collections import deque

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
BASE_URL = 'http://thirdpartyserver/api/numbers'  # Replace with actual third-party server URL
TIMEOUT = 0.5  # 500 ms timeout

# In-memory storage
stored_numbers = deque(maxlen=WINDOW_SIZE)

@app.route('/numbers/<numbecid>', methods=['GET'])
def get_numbers(numbecid):
    if numbecid not in ('p', 'f', 'e', 'r'):
        return json5({'error': 'Invalid number ID'}), 400

    try:
        # Fetch numbers from the third-party server
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/{numbecid}", timeout=TIMEOUT)
        elapsed_time = time.time() - start_time

        if elapsed_time > TIMEOUT or response.status_code != 200:
            return json5({'error': 'Failed to fetch data'}), 500
        
        # Process response
        new_numbers = response.json()
        if not isinstance(new_numbers, list):
            return json5({'error': 'Invalid data format from server'}), 500

        # Update stored numbers
        window_prev_state = list(stored_numbers)
        for number in new_numbers:
            if number not in stored_numbers:
                if len(stored_numbers) == WINDOW_SIZE:
                    stored_numbers.popleft()
                stored_numbers.append(number)

        # Compute the average if window is full
        average = None
        if len(stored_numbers) == WINDOW_SIZE:
            average = sum(stored_numbers) / len(stored_numbers)

        return json5({
            'windowPrevState': window_prev_state,
            'windowCurrState': list(stored_numbers),
            'average': average
        })

    except requests.RequestException:
        return json5({'error': 'Request exception occurred'}), 500

if __name__ == '__main__':
    app.run(port=9876)

