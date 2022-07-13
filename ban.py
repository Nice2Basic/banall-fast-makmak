from requests_cache import CachedSession
from datetime import timedelta
from threading import Thread
import os
import discord
import time
import json
import ctypes
import random


def route(method, endpoint, headers, body=None):
    base_url = "https://discord.com/api/v9"
    session = CachedSession(backend='memory', expire_after=timedelta(hours=1))
    if body:
        response = session.request(method=method.upper(
        ), url=base_url+endpoint, json=body, headers=headers)
    else:
        response = session.request(
            method=method.upper(), url=base_url+endpoint, headers=headers)
    return response


def ban(x, y, z, i=None):
    payload = {"delete_message_days": 0}
    if i:
        payload['reason'] = i
    bs = "\ "
    response = route(
        "PUT", f"/guilds/{y}/bans/{x}", {"Authorization": z}, payload)
    if response.status_code == 429:
        print(f"[{random.choice([f'{bs}'.replace(' ', ''), '/', '-', '|'])}] ratelimited for {response.json()['retry_after']}")
        time.sleep(response.json()['retry_after'])
        ban(x, y, z, i)
    else:
        if response.status_code in [200, 201, 204]:
            print(f"[>] banned {x}")


def massban(path, server, auth, reason=None):
    x = open(path)
    x = x.read()
    items = json.loads(x)
    for user in items["scraped"]:
        t = Thread(target=ban, args=(user, server, auth, reason,))
        t.start()
    _inital(server)


def validateToken(token):
    headers = {"Authorization": token}
    response = route("GET", "/users/@me", headers)
    if response.status_code in [200, 204, 201]:
        return "user", True
    else:
        headers = {"Authorization": f"Bot {token}"}
        response = route("GET", "/users/@me", headers)
        if response.status_code in [200, 204, 201]:
            return "bot", True
        else:
            return "invalid", False


client = discord.Client(intents=discord.Intents.all())

ctypes.windll.kernel32.SetConsoleTitleW("massban | FAST")
token = input("[?] token: ")


def _inital(server):
    os.system("cls")
    print("[1] - ban\n[2] - scrape")
    command = input("\n[?] command: ")
    if command not in ["1", "2"]:
        _inital(server)
    else:
        if command == "1":
            reason = input(f"[?] reason (null) if u don't want a reason: ")
            desc, data = validateToken(token)
            if desc == "user":
                auth = token
            elif desc == "bot":
                auth = f"Bot {token}"
            massban("sy/users.json", server.id, auth,
                    reason=reason if reason != "null" else None)
        elif command == "2":
            scraped = scrape(server)
            print(f"[!] scraped {scraped} member{'' if scraped == 1 else 's'}")
            time.sleep(0.5)
            _inital(server)


def scrape(server: discord.Guild):
    m = 0
    data = {"scraped": []}
    for x in range(int(server.member_count) - 1):
        m += 1
        data["scraped"].append(server.members[x].id)
    y = open("sy/users.json", "w")
    ifed = json.dumps(data, indent=4)
    y.write(ifed)
    return m


@client.event
async def on_ready():
    server = input("[?] server: ")
    try:
        server = client.get_guild(int(server))
        if not server:
            print("[!] invalid server")
        else:
            _inital(server)
    except Exception as e:
        print(f"[!] exception raised, {e}")

if __name__ == '__main__':
    message, boolean = validateToken(token)
    if message == "invalid" and boolean == False:
        print("[-] invalid token was passed")
    else:
        if message == "bot":
            try:
                client.run(token)
            except:
                print("[-] invalid token was passed")
        elif message == "user":
            try:
                client.run(token, bot=False)
            except:
                print("[-] invalid token was passed")