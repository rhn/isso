Marginalia
==========

Marginalia is a book exchange & discussion website based on the premise that 
you have to obtain the physical copy of the book to post.

Marginalia is based on [Isso](http://posativ.org/isso/).

Testing
-------

To test, generate a SSH key, then install vagrant and ansible. The test host will be created from scratch, with a new key every time, so put the following in your `~/.ssh/config`. **DO NOT USE THIS FOR PRODUCTION HOSTS**.

```
Host 192.168.121.140
  StrictHostKeyChecking no
```

Run tests with:

```
python3 ./tests/test.py
```

For reasons yet unknown, the ansible jobs may fail a couple of times.

You can also start a fresh testing VM with Marginalia installed by running:

```
python3 ./tests/manhole.py
```

Site generation
---------------

1. Create a virtualenv for isso
2. Activate it
3. `python3 marginalia/gensite.py ansible/site`

Tutorial
--------

### Prepare

Run tests first.

### Create basic site

Use site template from tests.

Copy `ansible/config.yaml` somewhere. **FIXME**

Run the site generator. **FIXME**

### Install marginalia

Prepare the target machine 

Adjust `ansible_inventory.ini`.

Production installation
-----------------------

See the test suite.

API
---

Marginalia introduces over isso API:

- access keys found inside books
- uri-independent thread IDs
- thread and comment ranking

License
-------

Marginalia is distributed under the terms of AGPL license. An exception is made to the Isso project, who can freely incorporate Marginalia's changes into their codebase.
