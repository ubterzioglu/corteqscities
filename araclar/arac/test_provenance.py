import unittest
from provenance import author_link, usable_author_url

class AuthorEvidenceTests(unittest.TestCase):
    def test_edit_and_license_links_are_not_author_profiles(self):
        for value in ['https://commons.wikimedia.org/wiki/User:Test?action=edit&redlink=1','https://creativecommons.org/licenses/by/4.0/','https://commons.wikimedia.org/w/index.php?title=User:Missing&action=edit']:
            self.assertFalse(usable_author_url(value))
    def test_real_link_survives_html_and_protocol_relative_url(self):
        self.assertEqual(author_link('<a href="//commons.wikimedia.org/wiki/User:Example">Example</a>','Example','https://commons.wikimedia.org/wiki/File:A.jpg'),'https://commons.wikimedia.org/wiki/User:Example')
    def test_missing_profile_does_not_invent_a_user_page(self):
        self.assertEqual(author_link('A real name','A real name','https://commons.wikimedia.org/wiki/File:A.jpg'),'')

if __name__=='__main__':unittest.main()
