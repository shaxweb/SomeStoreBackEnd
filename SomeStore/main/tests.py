import requests, json

url = "https://somestorebackend.onrender.com/create_product/"
headers = {"Content-Type": "application/json"}
data = json.dumps({
    "author": 1,
    "category": 1,
    "title": "Color",
    "description": "Just color",
    "price": 12,
    "tg_images": ["AgACAgIAAxkBAALqT2hwvgf6EAi84PaB9bbf1Dd1VlabAALw8DEb8bUpS5Hm89mFEEKCAQADAgADeQADNgQ"]
})

response = requests.post(url, headers=headers, data=data)
print(response.text)