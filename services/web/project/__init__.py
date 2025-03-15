#!/usr/bin/env python3
import socket
from flask import Flask, redirect, render_template, request
from ping3 import ping

app = Flask(__name__, static_folder="assets")

APP_TITLE = "ping"
PING_TIMEOUT = 5


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        ip_address = get_users_ip_address()
    else:
        ip_address = str(request.form["address"])

    return redirect("/" + ip_address)


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
    return request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)


def check_ping(address):

    try:

        result = ping(address, timeout=PING_TIMEOUT)
        result_ip = socket.gethostbyname(address)

    except Exception:

        return f"There was <strong>a problem</strong> while trying to ping {address}"

    if result:

        try:

            formatted_result = f"{result:.20f}"
            full_result = f"pong! {address} (<strong>{result_ip}</strong>) responded in <strong>{formatted_result}</strong> seconds"

        except Exception:

            full_result = f"There was <strong>no reply</strong> to your ping of {address}"

    else:

        full_result = f"There was <strong>no reply</strong> to your ping of {address}"

    return full_result


if __name__ == "__main__":
    app.run()
