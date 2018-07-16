UPDATE bots
SET redirect_of = (SELECT id FROM bots WHERE name = 'A-lú-mih-bot')
WHERE name = 'Luuvabot';

UPDATE bots
SET redirect_of = (SELECT id FROM bots WHERE name = 'DangSunBot')
WHERE name = 'DangSunFlood';

UPDATE bots
SET redirect_of = (SELECT id FROM bots WHERE name = 'DangSunBot2')
WHERE name = 'DangSunFlood2';

UPDATE bots
SET redirect_of = (SELECT id FROM bots WHERE name = 'DynBot Srv2')
WHERE name = 'DynamicBot Srv2';

UPDATE bots
SET redirect_of = (SELECT id FROM bots WHERE name = 'DimaBot')
WHERE name = 'Dima st bk bot';

UPDATE requests_for_permissions
SET bot_name = 'The Anomebot 3',
bot_url = 'www.wikidata.org/wiki/User:The_Anomebot'
WHERE bot_name = 'The Anomebot';

DELETE FROM bots
WHERE name = 'The Anomebot';

UPDATE requests_for_permissions
SET bot_url = 'www.wikidata.org/wiki/User:CellosaurusBot',
bot_has_red_link = 0
WHERE bot_name = CellosaurusBot
