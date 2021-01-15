import csv
from collections import OrderedDict

results = {}
curf_ = {}
states = {}
with open('district_overall_2018.csv', encoding='utf-8', mode='r') as file:
    reader = csv.reader(file)

    first_line = True
    for row in reader:
        if first_line:
            first_line = False
            continue
        state_name = row[1]
        total_votes = int(row[15])
        candidate_name = row[10]
        candidate_party = row[11]
        candidate_votes = int(row[14])
        candidate_vote_share = round((candidate_votes / total_votes) * 100, 2)

        district_num = [int(s) for s in row[7].split() if s.isdigit()][0]
        district_name = '{0}-{1}'.format(row[2], district_num)

        candidate = {
            'name': candidate_name,
            'party': candidate_party,
            'candidate_votes': candidate_votes,
            'vote_share': candidate_vote_share
        }

        district = {"candidates": [candidate], "district_name": district_name, "total_votes": row[15]}
        state = {district_num: district}

        if state_name not in states:
            states[state_name] = state
        elif district_num not in states[state_name]:
            states[state_name][district_num] = district
        elif candidate not in states[state_name][district_num]["candidates"]:
            states[state_name][district_num]["candidates"].append(candidate)


for state in states:
    state_results = {}
    for district in states[state]:
        curated = sorted(states[state][district]['candidates'], key=lambda t: t['vote_share'], reverse=True)
        victor = curated[0]
        district_results = {
            'district_name': states[state][district]['district_name'],
            'winner': victor['name'],
            'party': victor['party'],
            'candidate_votes': victor['candidate_votes'],
            'vote_share': victor['vote_share'],
            'total_votes': states[state][district]['total_votes']
        }
        if len(curated) > 1:
            loser = curated[1]
            margin = round(victor['vote_share'] - loser['vote_share'], 2)
            party = victor['party'][0].upper()
            district_results['winning_margin'] = ("{0}+{1}".format(party, margin))

        state_results[district] = district_results
    cur = dict(sorted(state_results.items(), key=lambda item: item[0]))
    results[state] = cur
print(dict(sorted(results.items(), key=lambda item: item[0])))





with open('2018_midterm_results.csv', encoding='utf-8', mode='w') as file:
   for state in states:
        for district in states[state]:
            writer = csv.DictWriter(file, results[state][district].keys())
            writer.writeheader()
            writer.writerows(results[state][district])




