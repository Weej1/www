# -*- coding: utf-8 -*-

import pymongo, bson
from heapq import nlargest
from operator import itemgetter
from collections import defaultdict
from time import time

from foofind.services.db.feedbackstore import FeedbackStore
from torrents.services.torrentsstore import TorrentsStore
from torrents.services.blacklists import Blacklists

def levenshtein(a,b,threshold):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    if m-n>threshold:
        return threshold+1

    current = range(n+1)
    for i in xrange(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in xrange(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
        if threshold and min(current)>threshold:
            return threshold+1
    return current[n]

def update_rankings(app):

    feedbackdb = FeedbackStore()
    feedbackdb.init_app(app)

    torrentsdb = TorrentsStore()
    torrentsdb.init_app(app, feedbackdb)

    blacklists = Blacklists()
    blacklists.load_data(torrentsdb.get_blacklists())


    rankings = torrentsdb.get_rankings()

    last_update = next(rankings.itervalues())["last_update"]

    searches = torrentsdb.get_searches(last_update)
    print "\n %d new searches: "%len(searches)

    if searches:
        new_last_update = max(s["t"] for s in searches)

        for ranking_name, ranking in rankings.iteritems():
            try:
                torrentsdb.verify_ranking_searches(ranking_name)

                # ranking info
                size = int(ranking["size"])
                category = ranking.get("category", None)
                relevance_factor = ranking["relevance_factor"]

                # ranking used to compare and create trends
                ranking_trends_name = ranking.get("trends", None)
                ranking_trends = rankings.get(ranking_trends_name, None)
                if ranking_trends:
                    ranking_trends_final_ranking = ranking_trends.get("final_ranking", None)
                    ranking_trends_norm_factor = ranking_trends.get("norm_factor", None)

                generate_trends = ranking_trends and ranking_trends_final_ranking and ranking_trends_norm_factor

                # calculate parameters for weights update
                ellapsed_time = new_last_update - ranking["last_update"]
                alpha = relevance_factor**(ellapsed_time/ranking["interval"])
                beta = (1 - alpha)/(ellapsed_time/60.)

                weight_threshold = beta * relevance_factor**(ranking["threshold_interval"]/float(ranking["interval"]))

                print "RANKING %s: i = %d, lu = %.2f, wt = %.6f, te = %.2f alpha = %.6f, beta=%.6f"%(ranking_name, ranking["interval"], new_last_update, weight_threshold, ellapsed_time, alpha, beta)

                # reduce weights (and add trends info if needed)
                torrentsdb.batch_ranking_searches(ranking_name, ranking_trends_name, generate_trends, alpha)

                # update weights
                for search in searches:

                    # category filter for ranking
                    if category and search["c"]!=category:
                        continue

                    # check blacklists
                    if blacklists.prepare_phrase(search["s"]) in blacklists:
                        continue

                    # normalize search
                    text = search["s"].lower().replace(".", " ")

                    # increase weight for this search
                    torrentsdb.update_ranking_searches(ranking_name, text, beta)

                # discard less popular searches and calculates normalization factor
                norm_factor = torrentsdb.clean_ranking_searches(ranking_name, size, weight_threshold)

                if norm_factor:
                    ranking["norm_factor"] = norm_factor
                else:
                    norm_factor = ranking.get("norm_factor",1)
                    print "WARNING: can't calculate normalization factor."

                # filter and regenerate new ranking
                ranking["final_ranking"] = final_ranking = []

                for search_row in torrentsdb.get_ranking_searches(ranking_name):

                    search = search_row["_id"]
                    weight = search_row["value"]["w"]

                    # double-check blacklists
                    if blacklists.prepare_phrase(search) in blacklists:
                        continue

                    # calculate trend for this search
                    if generate_trends:
                        weight_trend = search_row["value"].get("t", None)
                        trend = (weight*ranking_trends_norm_factor/norm_factor/weight_trend) if weight_trend else None
                        trend_pos = next((i for i,x in enumerate(ranking_trends_final_ranking) if x[0]==search), None)
                    else:
                        trend = trend_pos = None

                    # adds word to set for checks in next iterations
                    final_ranking.append((search, weight/norm_factor, trend, trend_pos))

                    # stops when the list has the right size
                    if len(final_ranking)>=size:
                        break

                # update ranking
                ranking["last_update"] = new_last_update

                torrentsdb.save_ranking(ranking)
            except BaseException as e:
                print "Error updating ranking '%s':"%ranking_name
                print type(e), e