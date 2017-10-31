import unittest

from gensite import *


class MDParsing(unittest.TestCase):
    md_meta = """---
meta: foo
---
# Title

[link](http://example.com)
"""
    nometa = """# Title

[link](http://example.com)
"""
    def test_split_content_nometa(self):
        meta, content = split_content(self.nometa)
        self.assertIsNone(meta)
        self.assertEqual(content, self.nometa)
        
    def test_split_content_meta(self):
        meta, content = split_content(self.md_meta)
        self.assertEqual(meta, 'meta: foo')
        self.assertEqual(content.rstrip(), """# Title

[link](http://example.com)""")
        
