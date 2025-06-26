# This script fetches the text models from AI Horde and saves them to a JSON file.

import requests

url = "https://aihorde.net/api/v2/stats/text/models"
r = requests.get(url)
r.raise_for_status()  # will puke if something went wrong
with open("RawModelUsageData.json", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved to text_models.json")
