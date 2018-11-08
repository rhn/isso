Installation
============

Marginalia provides ansible installation scripts for CentOS 7.

Preparation
-----------

Set up an inventory file, and put your host inside a group called `marginalia`.

Create a directory to store generated bookplate codes:

```
mkdir ../../bookplates
```

Use the `fresh.yml` playbook to set up the deploy user, the `hosting` playbook to set up dependencies, and the `users` playbook to set up users.

```
ansible-playbook -i inventory.ini ./fresh.yml
ansible-playbook -i inventory.ini ./hosting.yml
ansible-playbook -i inventory.ini ./users.yml
```

Fill in variables in the inventory for each host:

- `script_url`: base URL for fetching scripts. Default: `inventory_hostname`
- `api_url`: base URL for calling API. Default: `inventory_hostname + "/api"`
- `site_url`: base URL for the site and static elements. Deault: `inventory_hostname`
- `book_path`: part of URL after `site_url` where books will be found
- `post_path`: part of URL after `site_url` where book codes will be found
- `db_path`: database path
- `host_site_path`: path to unprocessed site contents
- `host_bookcodes_path`: path to place generated bookplate codes (must exist)
- `host_dist_path`: path where the Marginalia source tarball can be found

Installation and updating
-------------------------

```
cd isso
python3 ./setup.py sdist
cd ansible
ansible-playbook -i inventory.ini ./site2.yml
```
