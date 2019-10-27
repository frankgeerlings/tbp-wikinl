from mwparserfromhell import parse
import itertools, re

class Nomination(object):
  def find_pages(self, section):
    title = section.get(0).title
    art_in_title = [unicode(l.title) for l in parse(title).filter_wikilinks()]
    y = [x.params for x in section.filter_templates(matches = 'Links2|tbp-links')]
    art_in_linkstemplate = list(itertools.chain.from_iterable(y))

    return set(art_in_title + [unicode(a.value) for a in art_in_linkstemplate])

  @staticmethod
  def find_strikethrough(title):
    """
    >>> Nomination.find_strikethrough(u'== <s>Yes</s> ==')
    True

    >>> Nomination.find_strikethrough(u'== No ==')
    False

    """
    return re.search(ur'<s>(.*?)</s>', unicode(title)) is not None

  @staticmethod
  def find_r(regex, text):
    r = regex.search(text)
    if (not r is None):
      return (r.start(), r.group('user').strip())
    else:
      return None

  @staticmethod
  def find_first_signature(section):
    """
    >>> Nomination.find_first_signature('[[User:User name]]')
    u'User name'

    >>> Nomination.find_first_signature('[[Gebruiker:User name]]')
    u'User name'

    >>> Nomination.find_first_signature('{{User:User name/Handtekening}}')
    u'User name'

    >>> Nomination.find_first_signature('{{User:First/Handtekening}} [[User:Second]]')
    u'First'

    >>> Nomination.find_first_signature('[[Overleg_gebruiker:Daniuu | Daniuu]] 26 okt 2019 23:16 (CEST)')
    u'Daniuu'

    When there are no results, None is returned
    >>> any([ None, None, None])
    False

    >>> Nomination.find_first_signature('Blah blah blah') is None
    True
    """
    userR = re.compile(r'\[\[(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)(?:\|.*?\]\]|\]\])')
    talkR = re.compile(r'\[\[(?:[Oo]verleg[_ ]gebruiker):(?P<user>.*?)(?:\|.*?\]\]|\]\])')
    strictTemplateR = re.compile(r'\{\{(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)\/[Hh]andtekening\}\}')
    templateR = re.compile(r'\{\{(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)\/.*?\}\}')
    
    first = [
	Nomination.find_r(templateR, unicode(section)) ,
	Nomination.find_r(userR, unicode(section)) ,
	Nomination.find_r(talkR, unicode(section)) ,
	Nomination.find_r(strictTemplateR, unicode(section)) ]

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
    set([u'Title'])

    >>> Nomination(section('== [[First]] == \\n {{tbp-links|Second}}'), 'whatever').pages
    set([u'Second', u'First'])

    When a nomination title contains strikethrough (<s>) the nomination revoked flag is set

    >>> Nomination(section('== <s> [[Title]] </s>=='), 'whatever').revoked
    True

    When the title doesn't contain strikethrough the nomination flag isn't set

    >>> Nomination(section('== [[Title]] =='), 'whatever').revoked
    False

    Revoking a nomination will still have the nominated pages listed

    >>> Nomination(section('== <s> [[First]] </s> == \\n {{tbp-links|Second}}'), 'whatever').pages
    set([u'Second', u'First'])
    """
    title = section.get(0).title

    self.pages = self.find_pages(section)
    self.nominator = self.find_first_signature(section)
    self.revoked = self.find_strikethrough(title)
    self.wikilink = pagename + '#' + title.strip_code().strip()
