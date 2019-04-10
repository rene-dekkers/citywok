import libvirt
c = libvirt.open('qemu:///system')
v = c.listAllDomains()[0]
v.info()
