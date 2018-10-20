Development
===========

Use Vagrant for development and testing deployment.

To start a VM

```
vagrant up
ansible-playbook -i ./ansible_inventory.ini ../ansible/hosting.yml
```

To install in a VM (you may need to remove a stale SSH host entry)

```
ansible-playbook -i ./ansible_inventory.ini ../ansible/site2.yml
```

Likewise for updating the install.

Updating data
-------------

TODO
