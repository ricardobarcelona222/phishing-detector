from app.ml.predict import predict_url

urls = [
    "https://google.com",
    "https://paypal.com/login",
    "http://secure-paypal-login.verify-account.ru"
]

for url in urls:
    result = predict_url(url)
    print(f"URL: {url}")
    print(f"Resultado: {result}")
    print("-----")
