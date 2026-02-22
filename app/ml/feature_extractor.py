import re
from urllib.parse import urlparse


def extract_features(url: str):
    parsed = urlparse(url)

    hostname = parsed.hostname if parsed.hostname else ""
    path = parsed.path if parsed.path else ""

    features = {}

    # Longitud total URL
    features["length_url"] = len(url)

    # Longitud hostname
    features["length_hostname"] = len(hostname)

    # Número de puntos
    features["nb_dots"] = url.count(".")

    # Número de guiones
    features["nb_hyphens"] = url.count("-")

    # Número de @
    features["nb_at"] = url.count("@")

    # Número de /
    features["nb_slash"] = url.count("/")

    # Número de ?
    features["nb_qm"] = url.count("?")

    # Número de &
    features["nb_and"] = url.count("&")

    # Número de subdominios
    features["nb_subdomains"] = len(hostname.split(".")) - 2 if hostname else 0

    # Tiene https
    features["https_token"] = 1 if parsed.scheme == "https" else 0

    # Ratio dígitos en URL
    digits = sum(c.isdigit() for c in url)
    features["ratio_digits_url"] = digits / len(url) if len(url) > 0 else 0

    return features
