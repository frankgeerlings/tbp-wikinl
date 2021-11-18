from mwparserfromhell import parse
import itertools, re

class Nomination(object):
  def find_pages(self, section):
    title = section.get(0).title
    art_in_title = [str(l.title) for l in parse(title).filter_wikilinks()]
    y = [x.params for x in section.filter_templates(matches = 'Links2|tbp-links')]
    art_in_linkstemplate = list(itertools.chain.from_iterable(y))

    return set(art_in_title + [str(a.value) for a in art_in_linkstemplate])

  @staticmethod
  def find_strikethrough(title):
    """
    >>> Nomination.find_strikethrough('== <s>Yes</s> ==')
    True

    >>> Nomination.find_strikethrough('== No ==')
    False

    """
    return re.search(r'<s>(.*?)</s>', str(title)) is not None

  @staticmethod
  def find_r(regex, text):
    """
    This is a helper function that finds the last matching regex in a string.

    >>> Nomination.find_r(re.compile(r'(?P<user>\w)'), 'AB')
    (1, 'B')
    """
    matches = [i for i in regex.finditer(text)]

    if not any(matches):
      return None

    r = matches[-1]

    return (r.start(), r.group('user').strip())

  @staticmethod
  def find_first_date_offset(section):
    """
    >>> Nomination.find_first_date_offset('18 nov 2019 20:29 (CET)')
    0
    >>> Nomination.find_first_date_offset('')
    """
    firstDate = re.search(r'\d+ [a-z]{3} \d{4}', section)

    if firstDate is None:
      return None

    return firstDate.start()

  @staticmethod
  def text_up_to_and_including_first_comment(section):
    date_offset = Nomination.find_first_date_offset(section)
    if (date_offset is None):
      return section

    return section[0:date_offset]

  @staticmethod
  def find_last_signature(section):
    """
    >>> Nomination.find_last_signature('[[User:User name]]')
    'User name'

    >>> Nomination.find_last_signature('[[Gebruiker:User name]]')
    'User name'

    >>> Nomination.find_last_signature('{{User:User name/Handtekening}}')
    'User name'

    >>> Nomination.find_last_signature('{{User:First/Handtekening}} [[User:Second]]')
    'First'

    >>> Nomination.find_last_signature('[[Overleg_gebruiker:Daniuu | Daniuu]] 26 okt 2019 23:16 (CEST)')
    'Daniuu'

    When there are no results, None is returned
    >>> any([ None, None, None])
    False

    >>> Nomination.find_last_signature('Blah blah blah') is None
    True

    Regression test for the case reported in Phabricator ticket T238647
    >>> Nomination.find_last_signature('* Mogelijk wel relevant, zie [https://nl.wikipedia.org/wiki/Speciaal:VerwijzingenNaarHier/Bob_Winter hier], maar ernstig wiu. Was als nuweg genomineerd, maar lijkt niet aan de [[Wikipedia:Richtlijnen_voor_moderatoren#Een_pagina_direct_verwijderen|criteria]] te voldoen. Ping [[Gebruiker:Piet.Wijker|Piet.Wijker]] en [[Gebruiker:Rudolphous|Rudolphous]]. [[User:Wutsje|Wutsje]] 18 nov 2019 20:29 (CET)  And then stuff follows after the date, including perhaps more signatures: [[User:Demo|TestUser]][[Gebruiker:Rudolphous|Rudolphous]]')
    'Wutsje'
    """
    userR = re.compile(r'\[\[(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)(?:\|.*?\]\]|\]\])')
    talkR = re.compile(r'\[\[(?:[Oo]verleg[_ ]gebruiker):(?P<user>.*?)(?:\|.*?\]\]|\]\])')
    strictTemplateR = re.compile(r'\{\{(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)\/[Hh]andtekening\}\}')
    templateR = re.compile(r'\{\{(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)\/.*?\}\}')

    opening_sentence = Nomination.text_up_to_and_including_first_comment(str(section))

    first = [
	Nomination.find_r(templateR, opening_sentence) ,
	Nomination.find_r(userR, opening_sentence) ,
	Nomination.find_r(talkR, opening_sentence) ,
	Nomination.find_r(strictTemplateR, opening_sentence) ]

    """
    This handles the case where there are no signatures
    """
    if not any(first):
      return None

    return min([x for x in first if x is not None])[1]

  def __init__(self, section, pagename):
    """
    >>> section = lambda text: parse(text).get_sections(levels=[2], include_headings=True)[0]

    >>> Nomination(section('== [[Title]] =='), 'whatever').pages
    {'Title'}

    >>> Nomination(section('== [[First]] == \\n {{tbp-links|Second}}'), 'whatever').pages
    {'Second', 'First'}

    When a nomination title contains strikethrough (<s>) the nomination revoked flag is set

    >>> Nomination(section('== <s> [[Title]] </s>=='), 'whatever').revoked
    True

    When the title doesn't contain strikethrough the nomination flag isn't set

    >>> Nomination(section('== [[Title]] =='), 'whatever').revoked
    False

    Revoking a nomination will still have the nominated pages listed

    >>> Nomination(section('== <s> [[First]] </s> == \\n {{tbp-links|Second}}'), 'whatever').pages
    {'Second', 'First'}
    """
    title = section.get(0).title

    self.pages = self.find_pages(section)
    self.nominator = self.find_last_signature(section)
    self.revoked = self.find_strikethrough(title)
    self.wikilink = pagename + '#' + title.strip_code().strip()
