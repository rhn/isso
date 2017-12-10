Marginalia provides ansible installation scripts for CentOS 7.

Set up inventory with the variables:

- `script_url`: base URL for fetching scripts. Default: `inventory_hostname`
- `api_url`: base URL for calling API. Default: `inventory_hostname + "/api"`
- `site_url`: base URL for the site and static elements. Deault: `inventory_hostname`
- `book_path`: part of URL after `site_url` where books will be found
- `post_path`: part of URL after `site_url` where book codes will be found
- `db_path`: database site (generator only)

After each change:

```
cd isso
python3 ./setup.py sdist
cd ansible
ansible-playbook ./site2.yml
```
