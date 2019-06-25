# Initial Structure of Database (Sep 2018)

Please check out: https://github.com/FUB-HCC/wikidata-bot-request-analysis/blob/master/doc/doc.ipynb

___

# Changes
## Change Set 1 (Dec 2018) 

Problem:	Some of the bots have no user_id.
	
## Change Set 1: For these three cases we cannot add any user_id to the table.

* Wikimedia Bot (this is represented by column "is_extension_bot")
https://www.wikidata.org/wiki/User:127.0.0.1


* Bots without bot flag (this is represented in column "has_botflag" by zero)
Eflybot: https://www.wikidata.org/wiki/User:Eflybot
Global Economic Map Bot: https://www.wikidata.org/wiki/User:Global_Economic_Map_Bot


## Change Set 2: I added another column "redirect" that contains the user_id of the redirect.
SELECT * FROM bots WHERE redirect IS NOT null

* Redirect
DangSunBot: https://www.wikidata.org/wiki/User:DangSunBot (user_id 858760)
Luuvabot: https://www.wikidata.org/wiki/User:A-l%C3%BA-mih-bot
DangSunFlood2: https://www.wikidata.org/wiki/User:DangSunBot2
Dima st bk bot: https://www.wikidata.org/wiki/User:DimaBot
DynamicBot Srv2: https://www.wikidata.org/wiki/User:DynBot_Srv2

Luuvabot
bot_name:A-lú-mih-bot
user_id: 2102134

DangSunFlood2
bot_name: DangSunBot2
user_id: 1308724

Dima st bk bot
bot_name: DimaBot
user_id: 1143259

DynamicBot Srv2:
bot_name: DynBot Srv2
user_id: 141001

## Change Set 3: I added another column "is_removed" and added an "1".
SELECT * FROM bots WHERE is_removed==1

* Probably removed accounts
Epochs bot
Fabot
AviBot
RavenXBot2
Shankarbot


