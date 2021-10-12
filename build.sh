#!/usr/bin/bash
docker build -t localhost:5000/clip_site -f Dockerfile.app . && \
	docker build -t localhost:5000/clip_db -f Dockerfile.mysql . && \
	docker build -t localhost:5000/clip_worker -f Dockerfile.worker . && \
	docker build -t localhost:5000/clip_importer -f Dockerfile.importer . 

docker push localhost:5000/clip_site && \
	docker push localhost:5000/clip_db && \
	docker push localhost:5000/clip_worker && \
	docker push localhost:5000/clip_importer

