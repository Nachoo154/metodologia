import re
import uuid

import requests


def main():
    session = requests.Session()
    resp = session.get("http://127.0.0.1:8000/register/")
    print("GET status", resp.status_code)
    if resp.status_code != 200:
        print(resp.text[:1000])
        raise SystemExit(1)

    match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', resp.text)
    if not match:
        match = re.search(r'value=["\']([^"\']+)["\'] name=["\']csrfmiddlewaretoken["\']', resp.text)
    print("csrf match", bool(match))
    if not match:
        raise SystemExit("no csrf token")
    csrf_token = match.group(1)
    print("csrf token", csrf_token)

    email = f"carlos1234+{uuid.uuid4().hex[:8]}@gmail.com"
    payload = {
        "csrfmiddlewaretoken": csrf_token,
        "first_name": "Carlos",
        "last_name": "Perez",
        "email": email,
        "password": "Test1234!",
        "tel": "1234567890",
    }
    headers = {"Referer": "http://127.0.0.1:8000/register/"}
    post = session.post("http://127.0.0.1:8000/register/", data=payload, headers=headers)
    print("POST status", post.status_code)
    print("email used:", email)

    if 'class="error"' in post.text:
        match = re.search(r'<div class="error">([^<]+)</div>', post.text)
        print("ERROR:", match.group(1) if match else "error div found")
    elif 'class="success"' in post.text:
        match = re.search(r'<div class="success">([^<]+)</div>', post.text)
        print("SUCCESS:", match.group(1) if match else "success div found")
    else:
        print("RESPONSE PAGE:")
        print(post.text[:2000])


if __name__ == "__main__":
    main()
