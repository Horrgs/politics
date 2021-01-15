import csv
from collections import OrderedDict

results = []
curf_ = {}
with open('district_overall_2018.csv', encoding='utf-8', mode='r') as file:
    reader = csv.reader(file)
    states = {}
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

        candidate = {
            'name': candidate_name,
            'party': candidate_party,
            'votes': candidate_votes,
            'vote_share': candidate_vote_share
        }

        district_num = [int(s) for s in row[7].split() if s.isdigit()][0]
        district_name = '{0}-{1}'.format(row[2], district_num)
        district = {"candidates": [candidate], "district_name": district_name, "total_votes": row[15]}
        state = {district_num: district}
        if state_name not in states:
            states[state_name] = state
        elif district_name not in states[state_name]:
            states[state_name][district_num] = district

        elif candidate not in states[state_name][district_name]["candidates"]:
            states[state_name][district_num]["candidates"].append(candidate)

    for state in states:
        for district in states[state]:
            curated = sorted(states[state][district]['candidates'], key=lambda t: t['vote_share'], reverse=True)
            victor = curated[0]
            district_results = {
                'state': state,
                'district': district,
                'winner': victor['name'],
            }
            winner_msg = "The winner of {0} is {1} with a vote share of {2}. ".format(district, curated[0]['name'],
                                                                             curated[0]['vote_share'])
            margin_msg = ""
            if len(curated) > 1:
                loser = curated[1]
                margin_msg = ("Margin is {0} to {1}, result is {2}".format(victor['vote_share'], loser['vote_share'], (victor['vote_share'] - loser['vote_share'])))
                district_results['margin'] = (victor['vote_share'] - loser['vote_share'])
                winner_msg += "The second place person is {0} with {1} of the vote.".format(loser['name'], loser['vote_share'])
            results.append(district_results)
    curf_ = {}
    for state in states:
        cur = dict(sorted(states[state].items(), key=lambda item: item[0]))
        curf_[state] = cur


print(results)
curated_ = sorted(results, key=lambda district: district['district'])
with open('2018_midterm_results.csv', encoding='utf-8', mode='w') as file:
    writer = csv.DictWriter(file, results[0].keys())
    writer.writeheader()
    writer.writerows(curated_)





