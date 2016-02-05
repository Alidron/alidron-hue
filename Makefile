# Copyright (c) 2015-2016 Contributors as noted in the AUTHORS file
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

image_name = alidron/alidron-hue
rpi_image_name = alidron/rpi-alidron-hue
private_rpi_registry = neuron.local:6667

container_name = alidron-hue

network_name = host

run_args = -v $(CURDIR)/user:/usr/src/alidron-hue/user
exec_args = python alidron-hue.py

.PHONY: clean clean-dangling build build-rpi push push-rpi push-rpi-priv pull pull-rpi pull-rpi-priv run-bash run-bash-rpi run run-rpi run-cmd run-cmd-rpi stop logs

clean:
	docker rmi $(image_name) || true

clean-dangling:
	docker rmi `docker images -q -f dangling=true` || true

build: clean-dangling
	docker build --force-rm=true -t $(image_name) .

build-rpi: clean-dangling
	docker build --force-rm=true -t $(rpi_image_name) -f Dockerfile-rpi .

push:
	docker push $(image_name)

push-rpi:
	docker push $(rpi_image_name)

push-rpi-priv:
	docker tag -f $(rpi_image_name) $(private_rpi_registry)/$(rpi_image_name)
	docker push $(private_rpi_registry)/$(rpi_image_name)

pull:
	docker pull $(image_name)

pull-rpi:
	docker pull $(rpi_image_name)

pull-rpi-priv:
	docker pull $(private_rpi_registry)/$(rpi_image_name)
	docker tag -f $(private_rpi_registry)/$(rpi_image_name) $(rpi_image_name)

run-bash:
	docker run -it --rm --net=$(network_name) --name=$(container_name) $(run_args) $(image_name) bash

run-bash-rpi:
	docker run -it --rm --net=$(network_name) --name=$(container_name) $(run_args) $(rpi_image_name) bash

run:
	docker run -it --rm --net=$(network_name) --name=$(container_name) $(run_args) $(image_name) $(exec_args)

run-rpi:
	docker run -d --net=$(network_name) --name=$(container_name)-prod $(run_args) $(rpi_image_name) $(exec_args)

stop:
	docker stop -t 2 $(container_name)
	docker rm $(container_name)

logs:
	docker logs -f $(container_name)

exec:
	docker exec -it $(container_name) bash
