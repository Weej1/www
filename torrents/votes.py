#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator, math

VOTES = {"f1": "Verified", "f2": "Fake file", "f3": "Password protected", "f4": "Low quality", "f5": "Virus", "f6": "Bad"}
VERIFIED_VOTE = "f1"
GENERIC_BAD_VOTE = "f6"
REAL_VOTE_TYPES = 5

# votes and rating constants
TORRENTS_PROBS = {"f1": 0.50, "f2": 0.25, "f3": 0.05, "f4": 0.19, "f5": 0.01}
VERIFIED_THRESHOLD = 0.95
FLAG_THRESHOLD = 0.5
TRUSTED_FLAG_THRESHOLD = 0.6
HALF_PRIZE_SEEDS = 10


NORM_STEPS = 100
W_OK_BAD = 0.03     # inverse weight of ok votes for bad files
W_BAD_BAD = 0.0007  # inverse weight of bad votes for bad files
W_OK_OK = 0.0007    # inverse weight of ok votes for ok files
W_BAD_OK = 0.25     # inverse weight of bad votes for ok files

def prob_bad_wo_norm(bads, oks):
    return math.exp(- W_OK_BAD * oks*oks - W_BAD_BAD * bads*bads)

def prob_ok_wo_norm(bads, oks):
    return math.exp(- W_OK_OK * oks*oks - W_BAD_OK * bads*bads)

NORM_BAD = sum(prob_bad_wo_norm(bads,oks) for bads in xrange(NORM_STEPS) for oks in xrange(NORM_STEPS))
NORM_OK = sum(prob_ok_wo_norm(bads,oks) for bads in xrange(NORM_STEPS) for oks in xrange(NORM_STEPS))

def prob_bad(bads, oks):
    return prob_bad_wo_norm(bads, oks)/NORM_BAD

def prob_ok(bads, oks):
    return prob_ok_wo_norm(bads, oks)/NORM_OK


no_votes = None

def evaluate_file_votes(system, users):
    if not system and not users and no_votes:
        return no_votes

    # calculates system probs
    if system:
        system_vote = max(system.iteritems(), key=operator.itemgetter(1))

        # calculate system vote and "the rest" of system votes
        system_vote_norm = (system_vote[1]+100)/200.
        rest_vote_norm = (1.-system_vote_norm)/(REAL_VOTE_TYPES-1)

        system_probs = {vtype:(0.00001*p0 + 0.99999*(system_vote_norm if vtype==system_vote[0] else rest_vote_norm)) for vtype, p0 in TORRENTS_PROBS.iteritems()}
    else:
        system_probs = TORRENTS_PROBS

    # adds users votes to system probs
    extra_bad = users.get(GENERIC_BAD_VOTE,0)
    probs = {}
    for vtype in system_probs:
        if vtype==VERIFIED_VOTE: # ignore verified votes at this step
            continue

        votes_bad = users.get(vtype,0) + extra_bad
        votes_ok = users.get(VERIFIED_VOTE,0)
        pbad = prob_bad(votes_bad, votes_ok)
        pok = prob_ok(votes_bad, votes_ok)

        s = system_probs[vtype]
        probs[vtype] = pbad * s / (pbad * s + pok * (1 - s))

    val = reduce(operator.mul, [1-p for p in probs.itervalues()], 1)

    return val, sorted(probs.iteritems(), key=operator.itemgetter(1), reverse=True)

no_votes = evaluate_file_votes({},{})

def rate_torrent(data):
    # calculate torrent health
    try:
        seeds = float(data['md'].get('torrent:seeds',0))
    except:
        seeds = 0.
    try:
        leechs = float(data['md'].get('torrent:leechs',0))
    except:
        leechs = 0.
    health = min(1,(seeds*0.75+0.5)/(leechs+2))# int(0.2/(leechs+1.) if seeds==0 else min(1,(+1)/1.5/(+1)))

    # votes and flags
    vs = data.get("vs",{})
    system = vs.get("s", {})
    users = vs.get("u", {})
    votes_val, flags = evaluate_file_votes(system, users)

    # calculates file rating
    rating = health*votes_val

    # adds rating to torrents with many seeders and without negative flags
    if votes_val>=FLAG_THRESHOLD:
        rating = rating*.9 + (1-rating*.9)*seeds/(seeds+HALF_PRIZE_SEEDS)

    # add info to file
    res = {'seeds':seeds+.1/(1+leechs), 'content': votes_val, 'health': health, 'rating': rating, "votes": users}

    # adds flags
    if votes_val>VERIFIED_THRESHOLD:
        res["flag"] = [VERIFIED_VOTE, VOTES[VERIFIED_VOTE], votes_val]
    elif votes_val<FLAG_THRESHOLD:
        res["flag"] = [flags[0][0], VOTES[flags[0][0]], (1-votes_val)*flags[0][1]>TRUSTED_FLAG_THRESHOLD]

    return res

if __name__ == '__main__':
    import timeit

    print "Performance"
    print "No votes", timeit.timeit(lambda: evaluate_file_votes({}, {}), number=10000)
    print "System votes", timeit.timeit(lambda: evaluate_file_votes({"f1":60}, {}), number=10000)
    print "User votes", timeit.timeit(lambda: evaluate_file_votes({}, {"f1":10, "f3":23, "f2":12}), number=10000)
    print "Both votes", timeit.timeit(lambda: evaluate_file_votes({"f2":60}, {"f1":10, "f3":23, "f2":12}), number=10000)

    # evaluate for different system votes
    for system in [{}, {"f1":30}, {"f1":100}, {"f2":20}, {"f2":100}, {"f3":100}]:
        print system
        print "-"*30

        # no user votes
        print "No user:", evaluate_file_votes(system, {})

        # single type user votes
        for vtype in ["f1", "f2", "f3"]:
            for i in [1,2,3,5,7,9,15,20]:
                print "%d %s: %s"%(i, vtype, evaluate_file_votes(system, {vtype:i}))
            print

        # specific user cases votes
        for users in [{"f3":1, "f6":2}, {"f1":8, "f2":4}, {"f6":4}, {"f1":4, "f2":1}, {"f6":10, "f2":1}, {u'f1': 8, u'f2': 4, u'f6': 1}]:
            print "%s: %s"%(users, evaluate_file_votes(system, users))
        print
        print

    print rate_torrent({"md":{"torrent:seeds":20}})
    print rate_torrent({"md":{"torrent:seeds":5}, "vs":{"u":{"f1":100}}})
    print rate_torrent({"md":{"torrent:seeds":67, "torrents:leechs":7}, "vs":{"u":{"f3":1, "f6":2}}})
    print rate_torrent({"md":{'torrent:leechs': 74, 'torrent:seeds': 430}, "vs":{u'u': {u'f1': 27, u'f2': 3, u'f3': 1, u'f5': 1, u'f6': 8}}})
    print rate_torrent({"md":{'torrent:leechs': 10, 'torrent:seeds': 69}, "vs":{u'u': {u'f3': 2, u'f6': 5}}})
