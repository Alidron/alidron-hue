Philips Hue client for Alidron
==============================

[![build status](https://git.tinigrifi.org/ci/projects/9/status.png?ref=master)](https://git.tinigrifi.org/ci/projects/9?ref=master) [![Gitter](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/Alidron/talk)

This is a Philips Hue lightings client for Alidron.

Docker containers
=================

The Docker images are accessible on:
* x86: [alidron/alidron-hue](https://hub.docker.com/r/alidron/alidron-hue/)
* ARM/Raspberry Pi: [alidron/rpi-alidron-hue](https://hub.docker.com/r/alidron/rpi-alidron-hue/)

Dockerfiles are accessible from the Github repository:
* x86: [Dockerfile](https://github.com/Alidron/alidron-hue/blob/master/Dockerfile)
* ARM/Raspberry Pi: [Dockerfile](https://github.com/Alidron/alidron-hue/blob/master/Dockerfile-rpi)

Run
===

```
$ docker run -it --rm --net=host --name=alidron-hue -v `pwd`/user:/usr/src/alidron-hue/user alidron/alidron-hue python alidron-hue.py
```

License and contribution policy
===============================

This project is licensed under MPLv2.

To contribute, please, follow the [C4.1](http://rfc.zeromq.org/spec:22) contribution policy.
