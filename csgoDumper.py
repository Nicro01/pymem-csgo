import os
import requests
import json
from datetime import date
from github import Github

def file_get_contents(filename):
    with open(filename) as f:
        return f.read()

def send_files(datum, token):
    g = Github(token)
    repo = g.get_repo("Nicro01/CSGO_Auto_Dumper")
    files_list = ["csgo.cs", "csgo.hpp", "csgo.json", "csgo.min.json", "csgo.toml", "csgo.vb", "csgo.yaml", "csgo.py"]
    for x in files_list:
        print("Updating " + x)
        contents = repo.get_contents(x, ref="master")
        repo.update_file(contents.path, "✨ CS:GO ✨" + datum, file_get_contents(x), contents.sha, branch="master")

if __name__ == "__main__":
    print("Opening HazeDumper")
    hazedumper = requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json").json()

    with open("csgo.py","w") as f:
        for x in hazedumper["signatures"]:
            f.write(x + " = (" + hex(hazedumper["signatures"][x]) + ")\n")

        for x in hazedumper["netvars"]:
            f.write(x + " = (" + hex(hazedumper["netvars"][x]) + ")\n")
        f.close()

    token = "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"
    print("Uploading to Github")
    send_files(str(date.today()), token)
