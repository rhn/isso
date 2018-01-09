Marginalia
==========

Marginalia is a book exchange & discussion website based on the premise that 
you have to obtain the physical copy of the book to post.

Marginalia is based on [Isso](http://posativ.org/isso/).

Installation
------------

See Isso's documentation :)

Site generation
---------------

1. Create a virtualenv for isso
2. Activate it
3. `cd ansible/data/`
4. `python3 marginalia/gensite.py ansible/site`

API
---

Marginalia introduces:

- access keys found inside books
- uri-independent thread IDs
- thread and comment ranking

License
-------

Marginalia is distributed under the terms of AGPL license. An exception is made to the Isso project, who can freely incorporate Marginalia's changes into their codebase.
