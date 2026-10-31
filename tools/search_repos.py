# -*- coding: utf-8 -*-
import urllib.request
import json

queries = [
    "plants+vs+zombies+language:python",
    "plants-vs-zombies+assets",
    "pvz+assets",
    "python-plants-vs-zombies",
]

for q in queries:
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"=== Query: {q} (Total: {data.get('total_count')}) ===")
            for r in data.get("items", [])[:5]:
                print("  ", r["full_name"], "Stars:", r["stargazers_count"])
    except Exception as e:
        print(f"Error on {q}: {e}")
