from pprint import pprint
import pywikibot

def assemble_text(nominations):
  if len(nominations) == 1:
    page, nom = nominations[0]
    titles = u'Het gaat om [[%s]] dat is genomineerd door [[Gebruiker:%s|%s]].' % (page, nom.nominator, nom.nominator)
  else:
    titles = u'De genomineerde artikelen zijn: \n'
    for page, nom in nominations:
      titles += '* [[%s]] (aangemeld door [[Gebruiker:%s|%s]]' % (page, nom.nominator, nom.nominator)
  wikilink = nominations[0][1].wikilink
  message = u'{{subst:Automatische kennisgeving nominatie voor beoordeling|%s|%s|%s}} --~~~~' % (assemble_title(nominations), titles, wikilink)

  return message

def assemble_title(nominations):
  if len(nominations) == 1:
    return u'Beoordelingsnominatie [[%s]]' % nominations[0][0]
  else:
    return u'Beoordelingsnominatie van o.a. [[%s]]' % nominations[0][0]

def leave_notification(site, user, nominations, talk_page):
  try:
    summary = u'Nieuw onderwerp: /* %s */ Automatische melding van beoordelingsnominatie' % assemble_title(nominations)
    text = talk_page.get()
  except pywikibot.NoPage:
    summary = u'Welkom op Wikipedia; %s' % assemble_title(nominations)
    text = u'{{Welkomstbericht}}'

  text = text + '\n\n' + assemble_text(nominations)
  talk_page.text = text
  talk_page.save(summary=summary, minor=False, botflag=False)
