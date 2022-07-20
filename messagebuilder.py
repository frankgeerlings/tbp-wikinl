from pprint import pprint
import pywikibot
import re

def assemble_text(nominations):
  if len(nominations) == 1:
    page, nom = nominations[0]
    titles = 'Het gaat om [[%s]].' % page
  else:
    titles = 'De genomineerde artikelen zijn:'
    for page, nom in nominations:
      titles += '\n* [[%s]]' % page
  wikilink = nominations[0][1].wikilink
  message = '{{subst:Automatische kennisgeving nominatie voor beoordeling|%s|%s|%s}} --~~~~' % (assemble_title(nominations), titles, wikilink)

  return message

def safe_for_summary(text):
  """
  Removes wikilinks from a string so it can be used as a change summary string.

  >>> safe_for_summary('Nieuw onderwerp: /* [[SHTF]] */')
  'Nieuw onderwerp: /* SHTF */'
  """
  return re.sub(r'\[\[(.*?)\]\]', u"\\1", text)

def assemble_title(nominations):
  if len(nominations) == 1:
    return 'Beoordelingsnominatie [[%s]]' % nominations[0][0]
  else:
    return 'Beoordelingsnominatie van o.a. [[%s]]' % nominations[0][0]

def leave_notification(site, user, nominations, talk_page):
  try:
    summary = 'Nieuw onderwerp: /* %s */ Automatische melding van beoordelingsnominatie' % safe_for_summary(assemble_title(nominations))
    text = talk_page.get()
  except pywikibot.NoPage:
    summary = 'Welkom op Wikipedia; %s' % assemble_title(nominations)
    text = '{{Welkomstbericht}}'

  text = text + '\n\n' + assemble_text(nominations)
  talk_page.text = text

  try:
    talk_page.save(summary=summary, minor=False, botflag=False)
  except pywikibot.OtherPageSaveError:
    pass
