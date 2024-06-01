BOT_TOKEN = "7485751066:AAF8QIut4s-vjQ4FZCNmY8b6bAn7RZy8_vY"

ANIMALS_DATA = {
    "siyr": {
        "id": 1,
        "name": "Angus Cow",
        "price_per_jilik": 50000,  # Price in KZT
        "total_jiliks": 12,
        "current_jiliks": 0,
        "image_url": "https://kz.all.biz/img/kz/catalog/2302168.JPG",  # Placeholder image URL
        "full_image_url": "https://sogym.kz/gallery_gen/537e508ed104fcdbe5d4e46bddf56302_fit.jpg",  # Placeholder full image URL
    },
    "zhylqy": {
        "id": 2,
        "name": "Horse",
        "price_per_jilik": 50000,  # Price in KZT
        "total_jiliks": 12,
        "current_jiliks": 0,
        "image_url": "https://thehorse.com/wp-content/uploads/2018/02/horses-grazing-in-tall-grass.jpg",  # Placeholder image URL
        "full_image_url": "https://sogym.kz/gallery_gen/537e508ed104fcdbe5d4e46bddf56302_fit.jpg",  # Placeholder full image URL
    },
}

GENERAL_INFO = """
Welcome to our Collective Meat Ordering Bot!

We are dedicated to providing high-quality meat from trusted local producers. Our goal is to connect consumers directly with farmers, ensuring fresh and ethically sourced meat.

About Us:
- We work with local farms to bring you the best quality meat.
- All our animals are raised in a healthy and natural environment.
- We ensure ethical treatment of animals and sustainable farming practices.

How it Works:
1. Choose an option to see available animals for collective ordering.
2. Contribute a certain number of jiliks to the animal of your choice.
3. Once the total amount is collected, the meat will be prepared and delivered to you.

Thank you for supporting local farmers and ethical meat production!
"""

GENERAL_INFO_IMAGE_URL = "https://mir-s3-cdn-cf.behance.net/project_modules/max_3840/1cef5e18856979.562d374fe8ec4.jpg"  # Replace with your actual image URL

ORDER_DATA = {}  # Dictionary to hold order data temporarily
