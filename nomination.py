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
  def find_r(regex, text):
    r = regex.search(text)
    if (not r is None):
      return (r.start(), r.group('user'))
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

    When there are no results, None is returned
    >>> any([ None, None, None])
    False

    >>> Nomination.find_first_signature('Blah blah blah') is None
    True
    """
    userR = re.compile(r'\[\[(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)(?:\|.*?\]\]|\]\])')
    strictTemplateR = re.compile(r'\{\{(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)\/[Hh]andtekening\}\}')
    templateR = re.compile(r'\{\{(?:[Uu]ser|[Gg]ebruiker):(?P<user>.*?)\/.*?\}\}')
    
    first = [
	Nomination.find_r(templateR, unicode(section)) ,
	Nomination.find_r(userR, unicode(section)) ,
	Nomination.find_r(strictTemplateR, unicode(section)) ]

    """
    This handles the case where there are no signatures
    """
    if not any(first):
      return None

    return min([x for x in first if x is not None])[1]

  def __init__(self, section, pagename):
    self.pages = self.find_pages(section)
    self.nominator = self.find_first_signature(section)
    self.wikilink = pagename + '#' + section.get(0).title.strip_code().strip()
