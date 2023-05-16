from models.event import Event
from parsers import ApiParser
import os
from datetime import datetime, timedelta
from typing import Generator, Union
from models.event import Event
from parsers import ApiParser
import requests
from xml.etree import ElementTree as ET
import pymongo

SLEEP = os.getenv('SLEEP', 60)

INVERTED_DIRECTION = int(os.getenv('INVERTED_DIRECTION', 1))
PERCENTAGE_LIMIT = float(os.getenv('PERCENTAGE_LIMIT', 0))

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://lbizzarro:dkljhfa03489l@stg-mongodb01.oam.ltd:27017,stg-mongodb02.oam.ltd:27017,stg-mongodb03.oam.ltd:27017/?authSource=admin&replicaSet=staging&readPreference=secondaryPreferred&ssl=false')
structure1 = os.environ.get('structure1','http://62.138.8.207:90/testfeed/17/0')


class feedmakertwo(ApiParser):

    def __init__(self):

        super().__init__(
            bookmaker_id= 30,
            bookmaker_name='feedmaker',
            inverted_direction=INVERTED_DIRECTION,
            percentage_limit=PERCENTAGE_LIMIT,
            url=structure1,
            sleep=SLEEP,
            sports= {1: 1, 2: 2, 3: 5}
        )

    def read_and_point_xml(self):
        req = requests.get(self.url)
        if req.status_code == 200:
            root = ET.fromstring(req.text)
        return root

    def research_field(self) -> list:
        """ ITA:Questa funzione ricerca i valori dei campi dei dati relativi al feed. L'ordine seguito si basa sull'assegno
                 relativo al lavoro ed è quindi differente dall'ordine con cui andremo a salvare i dati. Tale ordine è il seguente:
                 match ID, data del match, nome dei competitor in cinque lingue, stato del match, sport ID, nome dello sport
                 ID categoria, nome della categoria in cinque lingue, ID del torneo, nome del torneo in cinque lingue.
                 Essa ritorna la lista degli eventi suddivisi in tuple ( lista di tuple di eventi )
             EN: This function searches the corresponding values on the field of the xml document. The order of the element
                 followed is the one we had from the work assignment, so it's different from the order or the storage data.
                 Output: a list of tuple( a list of sport events ).
             Српски:Ова функција претражује одговарајуће вредности у пољу кмл документа. Редослед елемента који следи је онај
                    који смо имали из радног задатка, тако да се разликује од редоследа или података о складиштењу.
             Излаз: листа тупле (листа спортских догађаја).
             िन्दी :यह फ़ंक्शन किसी XML दस्तावेज़ फ़ील्ड में मिलान मानों की खोज करता है। निम्नलिखित तत्व क्रम वही है जो हमारे पास कार्य फ़ंक्शन से था, इसलिए यह ऑर्डर या संग्रहण डेटा से अलग है।
             आउटपुट: टुपल्स की सूची (खेल आयोजनों की सूची)."""
        aams = None
        live = False
        back = None
        lay = None

        event = []
        translations =[]
        for sport in self.read_and_point_xml().findall('./Sports/Sport'):
            for Match in sport.findall('./Category/Tournament/Match'):
                matchID = Match.get('BetradarMatchID')
                match_date_time = Match.find('./Fixture/DateInfo/MatchDate').text
                compIdh = Match.find('./Fixture/Competitors')
                competitorID_Home = compIdh[0][0].get('ID')
                competitorID_Away = compIdh[1][0].get('ID')
                competitor_name_home_bet = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='1']/Text[@Language='BET']")[0].text
                competitor_name_home_en = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='1']/Text[@Language='en']")[0].text
                competitor_name_home_es = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='1']/Text[@Language='es']")[0].text
                competitor_name_home_it = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='1']/Text[@Language='it']")[0].text
                competitor_name_home_pt = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='1']/Text[@Language='pt']")[0].text
                competitor_name_away_bet = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='2']/Text[@Language='BET']")[0].text
                competitor_name_away_en = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='2']/Text[@Language='en']")[0].text
                competitor_name_away_es = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='2']/Text[@Language='es']")[0].text
                competitor_name_away_it = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='2']/Text[@Language='it']")[0].text
                competitor_name_away_pt = \
                Match.find("./Fixture/Competitors/Texts/Text[@Type='2']/Text[@Language='pt']")[0].text
                sportID = sport.get('BetradarSportID')
                sport_name = sport.find("./Texts/Text[@Language='BET']/Value").text
                sport_name_en = sport.find("./Texts/Text[@Language='en']/Value").text
                sport_name_es = sport.find("./Texts/Text[@Language='es']/Value").text
                sport_name_it = sport.find("./Texts/Text[@Language='it']/Value").text
                sport_name_pt = sport.find("./Texts/Text[@Language='pt']/Value").text
                categoryID = sport.find("./Category").get('BetradarCategoryID')
                category_name_bet = sport.find("./Category/Texts/Text[@Language='BET']/Value").text
                category_name_en = sport.find("./Category/Texts/Text[@Language='en']/Value").text
                category_name_es = sport.find("./Category/Texts/Text[@Language='es']/Value").text
                category_name_it = sport.find("./Category/Texts/Text[@Language='it']/Value").text
                category_name_pt = sport.find("./Category/Texts/Text[@Language='pt']/Value").text
                tournamentID = sport.find("./Category/Tournament").get('BetradarTournamentID')
                tournament_name_bet = sport.find("./Category/Tournament/Texts/Text[@Language='BET']/Value").text
                tournament_name_en = sport.find("./Category/Tournament/Texts/Text[@Language='en']/Value").text
                tournament_name_es = sport.find("./Category/Tournament/Texts/Text[@Language='es']/Value").text
                tournament_name_it = sport.find("./Category/Tournament/Texts/Text[@Language='it']/Value").text
                tournament_name_pt = sport.find("./Category/Tournament/Texts/Text[@Language='pt']/Value").text
                if Match.find('./Fixture/StatusInfo')[0].text == 0:
                    status_match = 'Active'
                else:
                    status_match = 'Disable'
                # Parte relativa al popolamento della lista
                # Creo una tupla che conterrà gli elementi degli eventi e li passo alla lsita
                t_event = (  match_date_time, competitorID_Home, competitor_name_home_bet, competitorID_Away, competitor_name_away_bet, tournamentID, tournament_name_bet, categoryID,
                            category_name_bet,sport_name, matchID, aams,status_match, live, back, lay, sportID )


                t_translations = (sportID, sport_name_en, sport_name_es, sport_name_it, sport_name_pt,
                                  competitorID_Home, competitor_name_home_en, competitor_name_home_es, competitor_name_home_it, competitor_name_home_pt,
                                  competitorID_Away,competitor_name_away_en, competitor_name_away_es, competitor_name_away_it, competitor_name_away_pt,
                                  categoryID,category_name_en, category_name_es, category_name_it, category_name_pt,
                                  tournamentID,tournament_name_en, tournament_name_es, tournament_name_it, tournament_name_pt,
                     )
                event.append(t_event)
                translations.append(t_translations)
        return event, translations

    def get_all_events(self) -> Generator:
        list_ev , list_sport = self.research_field()
        for match in list_ev:
            yield match

    def get_event(self, event: any, last_update: datetime) -> Event:
        for i in range(len(event)):
             match_id= int(event[10])
             awayId= int(event[3])
             awayName= event[5]
             categoryId= int(event[7])
             categoryName= event[8]
             date= datetime.strptime(event[0], '%Y-%m-%dT%H:%M:%S')
             homeId= int(event[1])
             homeName= event[2]
             sportId= int(event[16])
             sportName= event[9]
             status= event[12]
             tournamentId= int(event[5])
             tournamentName= event[6]
        return Event(_id=match_id,
                bookmaker_id=self.id,
                bookmaker_name=self.name,
                date=date,
                home_id=homeId,
                home_name=homeName,
                away_id=awayId,
                away_name=awayName,
                sport_id=sportId,
                sport_name=sportName,
                tournament_id=tournamentId,
                tournament_name=tournamentName,
                category_id=categoryId,
                category_name=categoryName,
                betradar_id=match_id,
                status=status,
                last_update=int(last_update.timestamp()),
            )

    def get_translations_mongo(self, translations:any)-> dict:
        """ EN: This function unpacks data from the list of translations and formats them to be stored
                       in MongoDB
                    Input parameters: A list of tuples. Each tuple is an event
                    Ouput: data to be stored in MongoDB """
        data_sp = {}
        data_cp_h = {}
        data_cp_a = {}
        data_cat = {}
        data_tourn = {}
        for i in range(len(translations)):
            sport_trs = {'bookmaker': 'feedmaker',
                         'id': int(translations[0]),
                         'type': 'sport',
                         'data': {'en': [translations[1]],
                                  'es': [translations[2]],
                                  'it': [translations[3]],
                                  'pt': [translations[4]]}}

            competitor_trs_home = {'bookmaker': 'feedmaker',
                                   'id': int(translations[5]),
                                   'type': 'competitor',
                                   'data': {'en': [translations[6]],
                                            'es': [translations[7]],
                                            'it': [translations[8]],
                                            'pt': [translations[9]]}}

            competitor_trs_away = {'bookmaker': 'feedmaker',
                                   'id': int(translations[10]),
                                   'type': 'competitor',
                                   'data': {'en': [translations[11]],
                                            'es': [translations[12]],
                                            'it': [translations[13]],
                                            'pt': [translations[14]]}}

            category_trs = {'bookmaker': 'feedmaker',
                            'id': int(translations[15]),
                            'type': 'category',
                            'data': {
                                'en': [translations[16]],
                                'es': [translations[17]],
                                'it': [translations[18]],
                                'pt': [translations[19]]}
                            }

            tournament_trs = {'bookmaker': 'feedmaker',
                              'id': int(translations[20]),
                              'type': 'tournament',
                              'data': {
                                  'en': [translations[21]],
                                  'es': [translations[22]],
                                  'it': [translations[23]],
                                  'pt': [translations[24]]}
                              }
            data_sp[i] = sport_trs
            data_cp_h[i] = competitor_trs_home
            data_cp_a[i] = competitor_trs_away
            data_cat[i] = category_trs
            data_tourn[i] = tournament_trs
        return data_sp, data_cp_h, data_cp_a, data_cat, data_tourn

    def store_mongo_translations(self,data_sp, data_cp_h, data_cp_a, data_cat, data_tourn):
        """ITA: Questa è la funzione di storage per MongoDB.
                   Parametri in input: data_sp = dizionario di dizionari ( i dizionari qui contenuti
                                             corrispondono alle traduzioni in Inglese, Spagnolo, Italiano e
                                             Portoghese dei nomi degli sport )
                                       data_cp_h = dizionario di dizionari ( i dizionari qui contenuti
                                             corrispondono alle traduzioni in Inglese, Spagnolo, Italiano e
                                             Portoghese dei nomi dei competitor che giocano in casa )
                                       data_cp_a = dizionario di dizionari ( i dizionari qui contenuti
                                             corrispondono alle traduzioni in Inglese, Spagnolo, Italiano e
                                             Portoghese dei nomi dei competitor che giocano fuori casa )
                                       data_cat = dizionario di dizionari ( i dizionari qui contenuti
                                             corrispondono alle traduzioni in Inglese, Spagnolo, Italiano e
                                             Portoghese dei nomi delle categorie )
                                       data_tourn = dizionario di dizionari ( i dizionari qui contenuti
                                             corrispondono alle traduzioni in Inglese, Spagnolo, Italiano e
                                             Portoghese dei nomi dei tornei )
                   EN: This function stores events on MongoDB.
                   Input parameter: data_sp = dictionary of dictionaries ( i.e. dictionaries are the translations
                                              of sport's names in English, Spanish, Italian and Portuguese )
                                    data_cp_h = dictionary of dictionaries ( i.e. dictionaries are the translations
                                                of home competitors' names in English, Spanish, Italian and Portuguese )
                                    data_cp_a = dictionary of dictionaries ( i.e. dictionaries are the translations
                                                of away competitors' names in English, Spanish, Italian and Portuguese )
                                    data_cat =  dictionary of dictionaries ( i.e. dictionaries are the translations
                                                of away categories' names in English, Spanish, Italian and Portuguese )
                                    data_tourn = dictionary of dictionaries ( i.e. dictionaries are the translations
                                                of away tournaments' names in English, Spanish, Italian and Portuguese )
                   Српски: Ово је функција складиштења за МонгоДБ.
                   Улазни параметри: дата_сп = речник речника (тј. речници су преводи назива спорта на енглески, шпански,
                                               италијански и португалски)
                                     дата_цп_х = речник речника (тј. речници су преводи имена домаћих такмичара на енглески,
                                                 шпански, италијански и португалски)
                                     дата_цп_а = речник речника (тј. речници су преводи имена гостујућих такмичара на енглеском,
                                                 шпанском, италијанском и португалском)
                                     дата_цат = дизионарио ди дизионари
                                     дата_тоурн = дизионарио ди дизионари

                   िन्दी : यह MongoDB के लिए स्टोरेज फंक्शन है।
                   इनपुट पैरामीटर: evn = शब्दकोशों का शब्दकोश (यहां मौजूद शब्दकोश उन घटनाओं के अनुरूप हैं जो MongoDB पर सहेजी जाएंगी)
                               data_sp = शब्दकोशों का शब्दकोश (खेल नामों का अनुवाद)
                               data_cp_h = शब्दकोशों का शब्दकोश (खिलाड़ियों के नामों का अनुवाद)
                               data_cp_a = शब्दकोशों का शब्दकोश (खिलाड़ियों के नामों का अनुवाद)
                               data_cat = शब्दकोशों का शब्दकोश (श्रेणी के नामों का अनुवाद)
                               data_tourn = शब्दकोशों का शब्दकोश (टूर्नामेंट के नामों का अनुवाद)"""

        dbconnection = pymongo.MongoClient(MONGO_URI)
        db = dbconnection["feedmakernew"]
        connection_two = db["translations"]
        for i in range(len(data_cp_h)):
            document_competitor_h = connection_two.insert_one(data_cp_h[i])
            print(document_competitor_h.inserted_id)
            document_competitor_a = connection_two.insert_one(data_cp_a[i])
            print(document_competitor_a.inserted_id)
        for j in range(len(data_sp)):
            id = data_sp[j].get('id')
            if connection_two.count_documents({'id': id}, limit=1)==0:
                document_sport=connection_two.insert_one(data_sp[j])
                print(document_sport.inserted_id)
        for i in range(len(data_cat)):
            id = data_cat[i].get('id')
            if connection_two.count_documents({'id': id})==0:
                document_category=connection_two.insert_one(data_cat[i])
                print(document_category.inserted_id)
        for k in range(len(data_tourn)):
            id = data_tourn[k].get('id')
            if connection_two.count_documents({'id': id}) == 0:
                document_tournament=connection_two.insert_one(data_tourn[k])
                print(document_tournament.inserted_id)

fe = feedmakertwo()
a = fe.get_all_events()
b = fe.get_event()


