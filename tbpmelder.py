from mwparserfromhell import parse
import pywikibot, messagebuilder
from nomination import Nomination
from time import gmtime, strftime

def today():
  return strftime('%Y%m%d', gmtime())

def talk_page(site, username):
  return pywikibot.Page(site, u'%s:%s' % (site.namespace(3), username))

def mentions(title, talkpage):
    "The lambda is because of titles that use regex-reserved characters such as ( and )"
    return any(talkpage.filter_wikilinks(matches=lambda x: x.title == title)) or any(talkpage.filter_templates(matches = 'Vvn'))

def notify_contributors(site, contributor_nom):
  "Notify contributors if they haven't already been notified"
  for user in contributor_nom:
    noms = contributor_nom[user]
    talk = talk_page(site, user)
    talkcode = parse(talk.text)
    remaining = [(page, nom) for page, nom in noms if not mentions(page, talkcode)]

    if not any(remaining):
      "No need to notify this user"
      continue

    messagebuilder.leave_notification(site, user, remaining, talk)

def major_contributors(site, page):
  try:
    rev1 = page.oldest_revision
    return [rev1.user]
    "TODO: Find contributors other than creator"
  except pywikibot.NoPage:
    "Page is already gone but that is ok"
    return []

def handle_nomination(site, nom, contributor_nom):

  for pagename in nom.pages:
    page = pywikibot.Page(site, pagename)
    originalpage = page

    "This regrettably is an if, not a while. That would allow a redirect loop (TODO: Safe while)"
    if page.isRedirectPage():
      page = page.getRedirectTarget()

    contributors = major_contributors(site, page)
    for contributor in contributors:
      if nom.nominator == contributor:
        continue

      noms = []
      if contributor in contributor_nom:
        noms = contributor_nom[contributor]

      noms.append((originalpage.title(), nom))
      contributor_nom[contributor] = noms

def main(*args):
  local_args = pywikibot.handle_args(args)
  site = pywikibot.Site(code="nl", fam="wikipedia")
  pagename = "Wikipedia:Te beoordelen pagina's/Toegevoegd " + today()

  page = pywikibot.Page(site, pagename)

  wikicode = parse(page.text)

  sections = wikicode.get_sections(levels=[2], include_headings=True)

  noms = [Nomination(section, pagename) for section in sections]

  contributor_nom = dict()
  for nom in noms:
    if not nom.revoked:
      handle_nomination(site, nom, contributor_nom)

  notify_contributors(site, contributor_nom)

if __name__ == "__main__":
  try:
    main()
  except Exception:
    pywikibot.error("Fatal error:", exc_info=True)
