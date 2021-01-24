# - *- coding: utf- 8 - *-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
#import requests
#import re
import json
#import isbnlib
#from isbnlib.registry import bibformatters
#from datetime import datetime
#import datetime as d
#import time
#import math
#import urllib
#from tqdm import tqdm
#from pyzbar import pyzbar
#import argparse
#import cv2
import random
import time
from deep_translator import (GoogleTranslator, single_detection)

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

def googleTrans(a, b, text):
  time.sleep(0.2)
  return GoogleTranslator(source=a, target=b).translate(text)

def info(update, context):
  text = """Täyskäännösbotti kääntää tekstejä komennolla '/kaanna käännettävä teksti'. Yksinkertaisimmillaan botti tunnistaa kielen ja kääntää sen neljän satunnaisen kielen kautta alkuperäiseen tunnistettuun kieleen. Konepellin alle voi kurkistaa lisäämällä sulut "()" vinoviivakomennon ja tekstin väliin. Lisäasetuksia voi lisätä sulkujen sisälle, esim.
• (fi) asettaa aloituskieleksi suomenkielen ja kääntää neljän satunnaisen kielen kautta takaisin suomenkieleen. Botti on välillä huono tunnistamaan kieliä, joten tätä kannattaa käyttää.
• (7) kääntää tekstin seitsemän satunnaisen kielen kautta.

Kenoviivakomennolla /laulu botti arpoo pakollisen ja kääntää sen. Laulut tukevat myös lisämääreitä täysin edellämainitulla tavalla, esim. '/laulu (0 estonian)'.

 - Advanced -
Kahden tai useamman termin syöttäminen sulkujen sisään asettaa koko kääntösarjan, esim.
• (en fi 2 estonian) aloituskieli englanti, kääntö en => fi, kääntö kahden satunnaisen kielen kautta, ja lopuksi kääntö viroksi.
• (2 en) numero alussa (myös nolla kelpaa): tunnistaa kielen ja kääntää kahden satunnaisen kielen kautta tekstin englanniksi.
• (en 5) numero lopussa (myös nolla kelpaa): botti palauttaa lopuksi tekstin alkuperäisellä kielelllä, tässä esimerkissä viiden satunnaisen kielen kautta englanniksi.
• (fi r) 'r' lopussa kääntää tekstin lopuksi satunnaiselle kielelle.
• (r fi) Vastaavasti 'r' alussa asettaa satunnaisen aloituskielen.

 - Bugit -
Botti ei osaa puhua mm. ruotsia, norjaa tai tanskaa. Ongelma on Lapan tavoittamattomissa, mutta saattaa korjaantua Python-pakettien päivittyessä.
"""
  commands = update.message.text
  commands = " ".join(commands.split(" ")[1:])
  commands = remove_spaces_from_front(commands)
  if commands == "":
    return update.message.reply_text(text)
  return update.message.reply_text(translate_commands(commands + text, True))

def translate_commands(input, print_option):
  
  no_spaces = input.replace(" ", "")
  
  if no_spaces[0] == "(" and len(input.split(")")) > 1:
    limit = 10 # limit for translations
    meta = [] # tähän kerätään käännökset yksi kerrallaan
    commands = input.split("(")[1].split(")")[0].split(" ")
    # Poistetaan tyhjät komennot (usea välimerkki peräkkäin) ja samalla asetetaan kaikki merkit pieniksi
    q = 0
    while q < len(commands):
      commands[q] = commands[q].lower()
      if commands[q] == "":
        commands.pop(q)
      else:
        q += 1
    # Tuetut kielet
    lang_dict = GoogleTranslator.get_supported_languages(as_dict=True)
    lang_longs = list(lang_dict.keys())
    lang_shorts = list(lang_dict.values())
    rev_lang_dict = {value : key for (key, value) in lang_dict.items()}
    
    # Muuta esim. "4" kokonaisluvuksi
    for q in range(len(commands)):
      try:
        commands[q] = int(commands[q])
      except:
        "nothing"
    
    # komennon jälkenen osuus
    text = ")".join(input.split(")")[1:])
    
    # kokeile, onko tekstikenttä tyhjä
    text = remove_spaces_from_front(text)
    if text == "":
      return "Ei käy. Yritä paremmin."
    
    if len(text) > 5000:
      return "Pöh too long, didn't read. Botin raja on 5000 merkkiä, sori."
    
    # jos komentorivi on tyhjä => 4 rand. kieltä
    if len(commands) == 0:
      commands.append(4)
    
    if len(commands) == 1 and isinstance(commands[-1], int) and commands[-1] == 0:
      return printcondition(text,meta,print_option)
    
    ### Eka komento, kontrolloi kielen tunnistusta
    if isinstance(commands[0], int):
      try:
        orig_lang = single_detection(text, api_key=koodit["tekstintunnistus"])
      except:
        return "Odottamaton käänne tekstintunnistuksessa. Yritä uudelleen."
      if commands[0] <= 0: # if zero, remove the number
        commands.pop(0)
      
    elif commands[0] in lang_shorts:
      orig_lang = commands[0]
      commands.pop(0)
      
    elif commands[0] in lang_longs:
      orig_lang = lang_dict[commands[0]]
      commands.pop(0)
      
    elif commands[0] == 'r':
      orig_lang = random.choice(lang_shorts)
      commands.pop(0)
      
    else: # tunnista kieli, jos komento on tuntematon
      try:
        orig_lang = single_detection(text, api_key=koodit["tekstintunnistus"])
      except:
        return "Odottamaton käänne tekstintunnistuksessa. Yritä uudelleen."
      commands.pop(0)
    
    prev_lang = orig_lang
    next_lang = orig_lang
    
    if not (orig_lang in lang_shorts):
      return "Teksti tunnistettiin kieleksi '" + orig_lang + "', mutta sitä ei löydy Googlesta. Määrittele aloituskieli, esim '\kaanna (fi) tämä on suomea'."
    
    # Jos komennossa oli vain yksi kieli, tee 4 randomia
    if len(commands) == 0:
      commands = [4]
    
    ### Keskellä olevat komennot
    while limit > 0 and len(commands) > 0 and( len(commands) > 1 or (isinstance(commands[-1], int) and commands[-1] > 0) ):
      if isinstance(commands[0], int): # if number -> random and number -= 1
        next_lang = pick_random_language(orig_lang, prev_lang, prev_lang)
        commands[0] -= 1
        if commands[0] <= 0: # if zero, remove the number
          commands.pop(0)
          
      elif commands[0] in lang_shorts:
        next_lang = commands[0]
        commands.pop(0)
        if next_lang == prev_lang:
          continue
        
      elif commands[0] in lang_longs:
        next_lang = lang_dict[commands[0]]
        commands.pop(0)
        if next_lang == prev_lang:
          continue
        
      else:
        next_lang = pick_random_language(orig_lang, prev_lang, prev_lang)
        commands.pop(0)
        
      if len(text) >= 5000:
        return "Ihan hyvä, mut koitappa vähän lyhempää tekstiä."
      try:
        text = googleTrans(prev_lang, next_lang, text)
      except:
        return "Odottamaton käänne. Yritä uudelleen."
      meta.append(rev_lang_dict[prev_lang] + " => " + rev_lang_dict[next_lang])
      prev_lang = next_lang
      limit -= 1
    
    if limit <= 0:
      meta.append("Saavutit kääntöjen määrän rajan, sori.")
    
    ### Viimeinen komento (jos sitä on jäljellä)
    if len(commands) > 0 and commands[-1] == 'r':
      next_lang = pick_random_language(prev_lang, prev_lang, prev_lang)
          
    elif len(commands) > 0 and commands[-1] in lang_longs:
      if lang_dict[commands[-1]] == prev_lang: # user input is the same with previous one
        return printcondition(text,meta,print_option)
      else:
        next_lang = lang_dict[commands[-1]]
        
    elif len(commands) > 0 and commands[-1] in lang_shorts:
      if commands[-1] == prev_lang: # user input is the same with previous one
        return printcondition(text,meta,print_option)
      else:
        next_lang = commands[-1]
        
    else:
      next_lang = orig_lang
    
    if len(text) >= 5000:
      return "Ihan hyvä, mut koitappa vähän lyhempää tekstiä."
    try:
      text = googleTrans(prev_lang, next_lang, text)
    except:
      return "Odottamaton käänne. Yritä uudelleen."
    meta.append(rev_lang_dict[prev_lang] + " => " + rev_lang_dict[next_lang])
    return printcondition(text,meta,print_option)
  else:
    return translate_commands("(4) " + input, False)

def printcondition(text,meta,print_option):
  if print_option:
    if len(meta) == 0:
      return("(Ei käännöksiä)" + "\n\n" + text)
    else:
      return("Käännökset:\n" + "\n".join(meta) + "\n\n" + text)
  else:
    return(text)

def remove_spaces_from_front(text):
  if text == "":
    return text
  while text[0] == " ":
    text = text[1:]
    if text == "":
      return text
  return text

def pick_random_language(orig_lang, prev_lang, next_lang):
  lang_dict = GoogleTranslator.get_supported_languages(as_dict=True)
  lang_shorts = list(lang_dict.values())
  while next_lang == prev_lang or next_lang == orig_lang:
    next_lang = random.choice(lang_shorts)
  return next_lang

def translate(update, context):
    text = update.message.text
    update.message.reply_text(translate_commands(text, True))

def translate_kenoviiva(update, context):
    text = update.message.text
    text = " ".join(text.split(" ")[1:])
    text = remove_spaces_from_front(text)
    if text == "":
      return
    update.message.reply_text(translate_commands(text, True))

def print_langs(update, context):
  lang_dict = GoogleTranslator.get_supported_languages(as_dict=True)
  text = []
  for key, value in lang_dict.items():
    if key.islower() and value.islower():
      text.append(key + " (" + value + ")")
  update.message.reply_text("Tuetut kielet: " + ", ".join(text) + ".")

def merimies(update, context):
  texts = ["""My Evaline

My Evaline,
say you'll be mine! Whisper to me honey you'll be mine! Way down yonder in the old corn field for you I'll pine. Sweeter than the honey to the honey bee, I love you, say you love me. Meet me in the shade of the old apple tree, My Eva, Iva, Ova, Evaline.
""", """Kaunehin maa

Maa kaunein maa on pohjoinen, missä metsiä pellot pelkää, karu, paatinen kylmä on pinta sen, ei lannista aura sen selkää,
mut uhmaten hongat harmaat ain sen taivahan ääriä saartaa,
ja yllä korpien vaikenevain, ja yllä korpien vaikenevain, sen pilvissä kotkat kaartaa.

Maa kaunein maa on metsien, maa kaukaisen, uinuvan haaveen, se sitoo mielemme hiljaisen laill' arvoituksen ja aaveen.
Se kutsuu, se kiehtoo, se vaatii luo sen puissa on loihtua, taikaa
ja synkän salon kankahat nuo, ja synkän salon kankahat nuo, ne laulua kummaa kaikaa.
""", """Suomalainen rukous

Siunaa ja varjele meitä, Korkein, kädelläs.
Kaitse ain kansamme teitä vyöttäen voimalla meitä
Heikkoja edessäs. Sulta on kaikki suuruus, henki sun hengestäs.

Tutkien sydämemme silmäs meihin luo.
Ettemme harhaan kääntyis, ettei kansamme nääntyis,
Silmäsi meihin luo. Alati synnyinmaalle, siipies suoja suo.
""", """Suomen laulu
Kuule, kuinka soitto kaikuu, Väinön kanteleesta raikuu!
Laulu Suomen on! Laulu Suomen on!
Kuule, hongat huokaileepi, kuule, kosket pauhaileepi!
Laulu Suomen on! Laulu Suomen on!

Kaikkialla ääni kaikuu, kaikkialla kielet raikuu.
Laulu Suomen on! Laulu Suomen on!
Sydäntä jos suotu sulle, murheess', ilossakin kuule
Suomen laulua! Suomen laulua!
""", """Ylioppilaslaulu

Kaikukoon nyt laulu maamme niin kuin ukko jyrisee.
Kaikki eespäin astukaamme, sydän lämmin sykkäilee.
Laulusta me voiman saamme, laulu syömmen aukaisee.

Siis nyt käsikkäissä teemme, laulain valan kallihin.
Veri, henki Suomellemme Terve, Maamme rakkahin.
Veren antain Suomellemme, teemme Veljet valan kallihin.
""", """Hyvät ystävät

Hyvät ystävät juhla voi alkaa, sankarille me nostamme maljaa!

Tääl ei juodakaan kolmosen kaljaa, meille viihdyn suo shampanja vain, trallalla.
Tääl ei juodakaan kolmosen kaljaa, meille viihdyn suo shampanja vain.

Hauska juomia kurkkuun on suistaa, siten teekkariaikoja muistaa.

Yhteinen juolalulumme luistaa, juhlamieli on parhaimmillaan, trallalla.
Yhteinen juolalulumme luistaa, juhlamieli on parhaimmillaan.
""", """Juomalaulu

Ei veteen lähtehellä saa veikot tirkistellä, vaan viini pikariin, vaan viini pikariin.

Ei vesiin voida luottaa, mut viini riemun tuottaa, siks' tirkistämme niin,
vain viini pikariin, (pikariin), pikariin, pikariin.
Vain viini pikariin, (pikariin), pikariin, pikariin.
Vain viini pikariin, vain viini pikariin, vain viini pikariin,
pikariin, pikariin, pikariin, pikariin.

Ei veteen lähtehellä saa veikot tirkistellä, vaan viini pikariin, vaan viini pikariin.

Ei vesiin voida luottaa, mut viina riemun tuottaa, siks' tirkistämme niin,
vain viina pikariin, (pikariin), pikariin, pikariin.
Vain viina pikariin, (pikariin), pikariin, pikariin.
Vain viina pikariin, vain viina pikariin, vain viina pikariin,
pikariin, pikariin, pikariin, pikariin.
""", """Kolmas

Nyt yksi juotu on ja toista kaadetaan, mut vatsa pohjaton, mut vatsa pohjaton, on vielä janoissaan.
Siis kolmas sille suo, siis kolmas sille suo, ja malja pohjahan nyt juo!
""", """Koskenkorva

Nostakaamme malja, Koskenkorvaa on. Väljentyköön kalja mallas kelvoton.
Riemuella suo, siispä veikko juo. Riemuella suo, siispä veikko juo.

Kalja voimallansa meitä innostaa, Koskenkorvan kanssa mielet nostattaa.
Lohdutusta tuo, siispä veikko juo. Lohdutusta tuo, siispä veikko juo.
""","""Viljaviinaa

Viljaviinaa maistetaan, viljaviinaa, siitä ryypyn saa!
Viljaviinaa, lauletaan, sillä kaukaiset aarteet me aukaistaan.

Viljaviinaa maistetaan, viljaviinaa, siitä ryypyn saa!
Viljaviinaa, trallalaa, sillä kaukaiset aarteet me aukaistaan.

Leijonaa toiset meille haluaa suosittaa, Koskenkorvaa, Vaakuna viinaa.
Kuinka on, jos Wyborova sitsimme juhlistaa? Onko Tasavalta, Alkuviina,
Metsästäjän, Kalastajan, Perinne, Tyrnävä, Smirnoff parempaa?

(Skåll!)

Viljaviinaa,

Viljaviinaa maistetaan, viljaviinaa, siitä ryypyn saa!
Viljaviinaa, trallalaa, sillä äänemme myöskin me aukaistaan.
Absolut!
""", """Juhannus

Minä avaan syömeni selälleen ja annan päivän paistaa, minä tahdon kylpeä joka veen ja joka marjan maistaa.

Minun mielessäni on juhannus ja juhla ja mittumaari, ja jos minä illoin itkenkin, niin siellä on sateenkaari.
""", """Kevätlaulu

Niitty jälleen vihannoipi, nurmi kukkii tuoksuen.

Peipon riemusävel soipi, leivo lentää laulellen.
Peipon riemusävel soipi, leivo lentää laulellen.

Metsä muuttuu ihanaksi, lemmen ääni kaikuvi.
Metsä muuttuu ihanaksi, lemmen ääni kaikuvi.

Paimen yltyy rohkeemmaksi, neitonen on hellempi.
Paimen yltyy rohkeemmaksi, neitonen on hellempi.

Neitonen on hellempi.
""", """Laulajain lippu

Lippusemme kohouupi taivahille sinisille.
Joka silmä riemastuupi, laulu lausuu sydämmille.
(P! K!)

Eespäin veljet käykäämme, riemu (viini) olkoon seuramme,.
Yli vuorten, laaksoin, järvein, metsäin laulu kaikukoon,
Hurraa, hurraa, hurraa, hurraa! Nyt laulu kaikukoon, hurraa!

Nyt kukka rannalla, maistella aiomma maljasta.
Siis sinne menkäämme, nyt riemuimme, nyt riemuimme.

El' itke neitosein! Ruusu ei kuolla saa poskelta.
Sylissäs valkamain, mä etsin vain, mä etsin vain.
""", """Mieslaulu

Pois voihke ja itkun hyrske, käy työhön ja toimintaan!
Pois hento ja toivoton tyrske, ei viel’ ole kuolema maan!
Ole kylmä kuin kallio jäinen ja saatanan itsepäinen
elinvoimasi ponnistaan, elinvoimasi ponnistaan.

Pois harkinta, anna mit’ annat! Mikä liiaksi kallist’ ois?
Jos säkkiä saiturin kannat, jäät kunniakaartista pois.
Pien’ itsesi anna ja siitä sinä kansasi suuruus niitä!
Se kaunista, suurta lois, se kaunista, suurta lois.
""", """Sirkka

Sirkka lauloi lystiksensä, oman intonsa ilossa, huviksensa hyräeli, metisellä mättähällä, simakukkien seassa.
Päivä paistoi nurmen nunnut, kukat kultaiset kedolla, katselivat, kuultelivat, kun hän laulella liritti.

”Mitä laulat laiska roisto, hullutuksia hyräilet? Teehän työtä; eihän vatsa täyty tyhjistä loruista; Raipat selkään semmoiselle”
Torui muuan muurahainen, ylen itara itikka, Sirkan syytöntä iloa.

Sirkka lauloi lystiksensä, oman intonsa ilossa, huviksensa hyräeli, metisellä mättähällä, simakukkien seassa.
""", """Merimiäste läksilaul

Ulos mailmaha viä meijä jäljetön diä
Merell laudottem bääll. Kauas pois pala miäl,
Kauas sinn, misä auring ai lämmindäs lua,
Misä huajuvap palmu meill varjoas sua.
Ko siällt tarppeks o olt, ni mek kotti jällt tlee.
Hiivuvee, haaluvee, hiivuvee.

Meri käy, must o yä, purjep paukku ja lyä,
Köyde vingu ja soi. Kapteen huuta: »Ohoi,
Ylös mastoihi reivaman goht joka miäs,
Ny o viimene hetk meijän dullk kukatiäs!»
Jumal tiätä, jos koska mek kotti jällt tlee.
Hiivuvee, haaluvee, hiivuvee.

Kyll se muuttu se retk; alka riammune hetk.
Niingon gomppassi neul meijä astian geul,
käändy pohjossi. Lämmiä maa jäävät taa,
Kodoranna me nähd saa ja syndymämaa.
Ilo siilo o suur, ko mek kotti jällt tlee.
Hiivuvee, haaluvee, hiivuvee.
""", """September

Märkä syys ja pehmee maa, tulee kuin paljo hedelmää jakaa.

Nyt sinä kylvä talvi siement, laske myös verta koska lystänt.

Sisällykset, suolet ja muu, ei lääkitä salli syyskuu.
""", """Kevätsointuja

Taas leivoset ilmassa leikkiä lyö, kevätvirsiä viidakko kaikaa.
Suli hanget ja nousi jo kukkien vyö. Sinilaine jo lyö ja jo valkeni yö.
Nyt on toivoon ja lempeen aikaa, nyt on toivoon ja lempeen aikaa.

Nyt rinnass' on lämpö, mi murtavi jään, joka huokuili henkeä hallan.
Ja se vaativi voittoa kirkkahan sään. Elon onnea laulaa se enteillään.
Kevättunteille tuottavi vallan, kevättunteille tuottavi vallan.

Nyt tunnen kuin sieluni siivet saisj a ma leivona nousta voisin.
Ja mun tahtoni talvesta ponnahtais ja mun riemuni oikean kaiun sais,
Ja ma oikea laulaja oisin, ja ma oikea laulaja oisin!
""", """Hän kulkevi kuin yli kukkien

Hän kulkevi kuin yli kukkien,
hän käy kuni sävelten siivin,
niin norjana notkuvi varsi sen,
kun vastahan vaiti mä hiivin.

Ja kunis mun voimani kukoistaa
ja soi minun soittoni täällä,
sinis laulujen laineilla käydä hän saa
ja kulkea kukkien päällä!
""", """Sukkalaulu

Sukkia valittaessa kannattaa aina tukeutua puvun väriin. Silloin sukat eivät missään tapauksessa näytä turhan räikeiltä.

Sukkien värin valitseminen myös kenkien mukaan johtaa yleensä hyvään lopputulokseen. Sukkien värin valitseminen myös kenkien mukaan johtaa yleensä kivaan lopputulokseen.
""", """Kaikille on Koskenkorva

Tempasikin, oo-o, tempasikin, oo-o.

Toisille jallu on juhlaa, toisista rommi paras on.
Toinen taas rahansa tuhlaa konjakin nautintohon.

Mut kaikille on Koskenkorva, juoma paras ja virkistävin.
Ai-jai-jai-ja-ai, Koskenkorva meidät mukaansa tempasikin.

Tempasikin, oo-o, tempasikin, oo-o, ...
Tša-tša-tša!
"""]
  text = random.choice(texts)
  commands = update.message.text
  commands = " ".join(commands.split(" ")[1:])
  commands = remove_spaces_from_front(commands)
  if commands == "" and text == texts[0]: # enkunkieliset
    return update.message.reply_text(translate_commands("(en) " + text, False))
  elif commands == "": # suomenkieliset
    return update.message.reply_text(translate_commands("(fi) " + text, False))
  return update.message.reply_text(translate_commands(commands + text, True))
  
def main():
  
  # Create Updater object and attach dispatcher to it
  updater = Updater(koodit["kääntöbot"])
  dispatcher = updater.dispatcher
  print("Bot started")

  # Add command handler to dispatcher
  kenoviiva_translate_handler = CommandHandler('kaanna',translate_kenoviiva)
  info_handler = CommandHandler('start',info)
  langs_handler = CommandHandler('kielet',print_langs)
  merimies_handler = CommandHandler('laulu',merimies)
  
  #translate_handler    = MessageHandler(Filters.text, translate)
  
  dispatcher.add_handler(info_handler)
  dispatcher.add_handler(langs_handler)
  dispatcher.add_handler(kenoviiva_translate_handler)
  dispatcher.add_handler(merimies_handler)
  
  #dispatcher.add_handler(translate_handler)

  # Start the bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C
  updater.idle()

if __name__ == '__main__':
  main()
