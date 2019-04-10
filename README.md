#Description

This project is started to gain knowledge about the following items:

* flask
* flask api
* flask blueprints
* spice
* spicy html5

#Project

Citywok is a web GUI to manage your virtual environment. The spice-html5 t is implemented to attach to grapical console via html5.

The frontend is running on docker.

Only a small python api service is needed (backend) on the hypervisor. Your hypervisor has to support libvirt (kvm, xen, https://libvirt.org/drivers.html).

There is a built-in support for plugins that is based on flask blueprints. For example: https://github.com/rene-dekkers/citywok/tree/master/plugins/jenkins 

#TODO

* Automatically deployable
* More generic configuration
* Nginx reverse websocket proxy in front of websockify