from urllib.request import urlopen

from bs4 import BeautifulSoup
from nltk.corpus import wordnet

start = "Reindeer"
goal = "Flying Saucer"
satisfiablePercent = .75
wiki = "https://en.wikipedia.org/wiki/"
next_from_start = ""
next_from_goal = ""


def next_page(page, visited):
    url = wiki
    url += page
    website = urlopen(url)
    html = website.read()
    soup = BeautifulSoup(html, "html.parser")
    links = soup.findAll('a', href=True)
    current_best = ["", -1]
    for link in links:
        link = link['href']
        if not (link[:5] != "/wiki" or link[:-3] == ("JPG" or "jpg" or "png") or (
                len(link) >= 14 and link[6:14] == "Category") or (len(link) >= 16 and link[6:16] == "Wikipedia:") or (
                        len(link) >= 14 and link[6:14] == "Special:") or (len(link) >= 10 and link[6:10] == "File") or (
                        len(link) >= 13 and link[6:13] == "Portal:") or (
                        len(link) >= 15 and link[6:15] == "Main_Page") or (
                        len(link) >= 10 and link[6:10] == "Help") or (
                        len(link) > 16 and link[-16] == "(disambiguation)")):
            link = link[6:]
            if link not in visited and link == goal:
                return link
            synsets = wordnet.synsets(link)
            if synsets and link not in visited:
                w1 = synsets[0]
                score = w1.wup_similarity(goal_synset)
                if score >= satisfiablePercent:
                    return link
                elif score > current_best[1]:
                    current_best[0] = link
                    current_best[1] = score
    return current_best[0]


def bidirectional_wall(next_start, next_goal, s_v, g_v):
    global next_from_goal, next_from_start, satisfiablePercent
    keep_going = True
    if s_v:
        start_visited = s_v
    else:
        start_visited = [next_start]
    if g_v:
        goal_visited = g_v
    else:
        goal_visited = [next_goal]
    if start:
        if next_start == goal:
            total = len(start_visited)
            print("You can reach the goal in " + str(total - 1) + " clicks.")
            print(start_visited)
            print_wiki_links(start_visited)
            keep_going = False
        if next_start in goal_visited and keep_going:
            i = goal_visited.index(next_start)
            goal_visited = goal_visited[:i]
            goal_visited = goal_visited[::-1]
            path = start_visited
            path.extend(goal_visited[:i + 1])
            total = len(path) - 2
            print("You can reach the goal in " + str(total) + " clicks.")
            print(path)
            print_wiki_links(path)
            keep_going = False
        else:
            next_from_start = next_page(next_start, start_visited)
            retries = 5
            while next_from_start == "" and retries > 0:
                satisfiablePercent -= 0.08
                next_from_start = next_page(next_start, start_visited)
                retries -= 1
                print(
                    "Retrying with next_start: " + str(next_start) + ", start_visited: " + str(start_visited) +
                    ", satisfiablePercent: " + str(satisfiablePercent))
            if next_from_start == "":
                raise Exception("Unable to find a path")
            start_visited.append(next_from_start)
    if keep_going:
        if next_goal in start_visited:
            r = start_visited.index(next_goal)
            goal_visited = goal_visited[::-1]
            path = start_visited[:r + 1]
            path.extend(goal_visited[1:])
            total = len(path) - 2
            print("You can reach the goal in " + str(total) + " clicks.")
            print(path)
            print_wiki_links(path)
            keep_going = False
        else:
            next_from_goal = next_page(next_goal, goal_visited)
            goal_visited.append(next_from_goal)
    if keep_going:
        if next_from_start != "":
            print("next_from_start: " + next_from_start)
        if next_from_goal != "":
            print("next_from_goal: " + next_from_goal)
        bidirectional_wall(next_from_start, next_from_goal,
                           start_visited, goal_visited)


def print_wiki_links(visited_strings):
    for item in visited_strings:
        print(wiki + item)


def multiple_word_wiki_link(target_words):
    target_parts = target_words.split(" ")
    is_first = True
    result = ""
    sep = ""
    for part in target_parts:
        if is_first:
            is_first = False
        else:
            sep = "_"
            part = part.lower()
        result = result + sep + part
    return result


if ' ' in goal:
    goal = multiple_word_wiki_link(goal)
if ' ' in start:
    start = multiple_word_wiki_link(start)

print("goal_string: " + goal)
goal_synset = wordnet.synset(goal + ".n.01")
bidirectional_wall(start, goal, [], [])
