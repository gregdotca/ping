#!/usr/bin/env python3
import ipaddress
import socket
from urllib.parse import quote
from flask import Flask, redirect, render_template, request
from markupsafe import Markup
from ping3 import ping

app = Flask(__name__, static_folder="assets")

APP_TITLE = "ping"
PING_TIMEOUT = 5


@app.route("/", methods=["GET", "POST"])
def home():
    # prefill the visitor's IP without pinging it, since some IPs take
    # the full timeout to fail and the first page load would hang
    if request.method == "GET":
        return display_homepage(get_users_ip_address(), "")

    ip_address = str(request.form["address"])

    return redirect("/" + quote(ip_address, safe=""))


@app.route("/<address>", methods=["GET"])
def lookup(address):
    ping_result = check_ping(address)
    return display_homepage(address, ping_result)


def display_homepage(address, page_body):
    return render_template(
        "home.html",
        app_title=APP_TITLE,
        address=address,
        page_body=page_body,
    )


def get_users_ip_address():
    # a proxy chain looks like "client, proxy1, proxy2"
    forwarded_for = request.environ.get("HTTP_X_FORWARDED_FOR", "")
    client_ip = forwarded_for.split(",")[0].strip()
    return client_ip or request.remote_addr


def is_ipv6_address(address):
    try:
        return ipaddress.ip_address(address).version == 6
    except ValueError:
        return False


def check_ping(address):

    # gethostbyname() and the container network are IPv4-only
    if is_ipv6_address(address):

        return Markup("Sorry, IPv6 addresses like {} <strong>aren't supported</strong> yet").format(address)

    try:

        result_ip = socket.gethostbyname(address)

    except Exception:

        return Markup("There was <strong>a problem</strong> while trying to ping {}").format(address)

    # refuse loopback, private, link-local, and other non-public addresses,
    # so visitors can't map which hosts on the server's networks are up
    if not ipaddress.ip_address(result_ip).is_global:

        return Markup("Sorry, {} <strong>isn't a public address</strong>, so it can't be pinged").format(address)

    # ping the IP that was checked, not the name, so a second DNS lookup
    # can't swap in a private address
    try:

        result = ping(result_ip, timeout=PING_TIMEOUT)

    except Exception:

        return Markup("There was <strong>a problem</strong> while trying to ping {}").format(address)

    # ping3 returns the delay in seconds, or None/False when there's no
    # reply; checking the type keeps a 0.0 delay from counting as no reply
    if not isinstance(result, float):

        return Markup("There was <strong>no reply</strong> to your ping of {}").format(address)

    milliseconds = f"{result * 1000:.2f}"

    if address == result_ip:

        return Markup("pong! {} responded in <strong>{}</strong> ms").format(address, milliseconds)

    return Markup("pong! {} (<strong>{}</strong>) responded in <strong>{}</strong> ms").format(address, result_ip, milliseconds)


if __name__ == "__main__":
    app.run()
