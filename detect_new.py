import scraperwiki

results = scraperwiki.sql.select("count(*) as count,date FROM data group by date order by date ")

for result in results:
    print(result['date'],result['count'])
