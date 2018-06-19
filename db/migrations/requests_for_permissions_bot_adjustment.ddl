UPDATE requests_for_permissions
SET bot = 'www.wikidata.org/wiki/User:Innocent_bot'
WHERE bot = 'www.wikidata.org/wiki/User:/wiki/Wikidata:Requests_for_permissions/Innocent_bot_2';

UPDATE requests_for_permissions
SET bot = 'https://www.wikidata.org/wiki/User:Theo%27s_Little_Bot'
WHERE bot = 'www.wikidata.org/wiki/User:/wiki/Wikidata:Requests_for_permissions/Theo%27s_Little_Bot';

UPDATE requests_for_permissions
SET bot_name = 'Innocent bot'
WHERE bot_name = 'Wikidata:Requests for permissions/Innocent bot';

UPDATE requests_for_permissions
SET bot_name = 'Theo%27s Little Bot'
WHERE bot_name = 'Wikidata:Requests for permissions/Theo%27s Little Bot';

UPDATE requests_for_permissions
SET bot_name = 'CellosaurusBot'
WHERE bot_name = '/w/index.php?title=CellosaurusBot';

UPDATE bots
SET name = 'Theo%27s Little Bot'
WHERE name = 'Wikidata:Requests for permissions/Theo%27s Little Bot';

DELETE FROM bots
WHERE name IN ('User talk:MediaWiki message delivery', 'User talk:Mro-bot', 'User talk:SKbot', 'User talk:Strainubot', 'User talk:Xaris333Bot', '/w/index.php?title=CellosaurusBot', 'Wikidata:Requests for permissions/Innocent bot')