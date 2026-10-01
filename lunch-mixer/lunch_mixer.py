"""
Monthly Company Lunch Mixer
---------------------------
Builds lunch groups so that people meet colleagues they have NOT met before,
from DIFFERENT teams, and so that new joiners are spread across groups.

Usage:
    python lunch_mixer.py --employees employees.csv --history history.csv \
        --group-size 5 --month 2026-10 --output lunch_groups_2026-10.csv

employees.csv : name,email,team,start_date          (start_date = YYYY-MM-DD)
history.csv   : month,group_id,name                 (past lunches; may be empty/missing)
All data in this repo is fictional.
"""
import argparse, csv, itertools, math, os, random
from datetime import date, datetime

# Cost weights: the lower the total cost, the better the grouping.
W_ALREADY_MET = 10   # two people who already shared a lunch
W_SAME_TEAM = 3      # two people from the same team
W_NO_NEWCOMER = 6    # a group without any new joiner (when newcomers exist)
W_TOO_MANY_NEW = 2   # more than 2 new joiners in one group (spread them out)
NEW_JOINER_MONTHS = 6


def read_csv(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_new(start_date, today):
    d = datetime.strptime(start_date, "%Y-%m-%d").date()
    return (today.year - d.year) * 12 + (today.month - d.month) < NEW_JOINER_MONTHS


def met_pairs(history):
    """Set of frozenset({a, b}) for everyone who already shared a group."""
    groups = {}
    for r in history:
        groups.setdefault((r["month"], r["group_id"]), []).append(r["name"])
    pairs = set()
    for members in groups.values():
        for a, b in itertools.combinations(members, 2):
            pairs.add(frozenset((a, b)))
    return pairs


def split_sizes(n, size):
    """Even group sizes close to the target (e.g. 11 people, size 5 -> 4,4,3)."""
    k = max(1, math.ceil(n / size))
    base, extra = divmod(n, k)
    return [base + (1 if i < extra else 0) for i in range(k)]


def group_cost(group, info, met, has_new_anywhere):
    cost = 0
    for a, b in itertools.combinations(group, 2):
        if frozenset((a, b)) in met:
            cost += W_ALREADY_MET
        if info[a]["team"] == info[b]["team"]:
            cost += W_SAME_TEAM
    n_new = sum(info[p]["new"] for p in group)
    if has_new_anywhere and n_new == 0:
        cost += W_NO_NEWCOMER
    if n_new > 2:
        cost += W_TOO_MANY_NEW * (n_new - 2)
    return cost


def total_cost(groups, info, met, has_new):
    return sum(group_cost(g, info, met, has_new) for g in groups)


def build_groups(names, info, met, size, seed=42, restarts=30, iterations=3000):
    rng = random.Random(seed)
    sizes = split_sizes(len(names), size)
    has_new = any(info[n]["new"] for n in names)
    best, best_cost = None, float("inf")
    for _ in range(restarts):
        pool = names[:]
        rng.shuffle(pool)
        groups, i = [], 0
        for s in sizes:
            groups.append(pool[i:i + s]); i += s
        cost = total_cost(groups, info, met, has_new)
        for _ in range(iterations):          # hill-climbing: swap two people
            g1, g2 = rng.sample(range(len(groups)), 2) if len(groups) > 1 else (0, 0)
            if g1 == g2:
                break
            i1, i2 = rng.randrange(len(groups[g1])), rng.randrange(len(groups[g2]))
            groups[g1][i1], groups[g2][i2] = groups[g2][i2], groups[g1][i1]
            new_cost = total_cost(groups, info, met, has_new)
            if new_cost <= cost:
                cost = new_cost
            else:                              # undo the swap
                groups[g1][i1], groups[g2][i2] = groups[g2][i2], groups[g1][i1]
        if cost < best_cost:
            best, best_cost = [g[:] for g in groups], cost
    return best, best_cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--employees", required=True)
    ap.add_argument("--history", default=None)
    ap.add_argument("--group-size", type=int, default=5)
    ap.add_argument("--month", default=date.today().strftime("%Y-%m"))
    ap.add_argument("--output", default=None)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    today = date.today()
    employees = read_csv(a.employees)
    info = {e["name"]: {"team": e["team"], "email": e["email"],
                        "new": is_new(e["start_date"], today)} for e in employees}
    met = met_pairs(read_csv(a.history))
    groups, cost = build_groups(list(info), info, met, a.group_size, seed=a.seed)

    # Report
    repeat_pairs = sum(frozenset(p) in met for g in groups for p in itertools.combinations(g, 2))
    same_team = sum(info[x]["team"] == info[y]["team"] for g in groups for x, y in itertools.combinations(g, 2))
    print(f"{len(info)} people, {len(groups)} groups | repeat pairs: {repeat_pairs} | same-team pairs: {same_team}")

    out = a.output or f"lunch_groups_{a.month}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["month", "group_id", "name", "email", "team", "new_joiner"])
        for gi, g in enumerate(groups, 1):
            for p in g:
                w.writerow([a.month, f"G{gi}", p, info[p]["email"], info[p]["team"], "yes" if info[p]["new"] else "no"])
    print("Saved:", out)


if __name__ == "__main__":
    main()
