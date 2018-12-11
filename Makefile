help:
	@echo "start  - builds and starts services in dev mode"
	@echo "stop   - stop all running containers belonging to the project"
	@echo "test   - runs tests in debug mode (able to use pdb breakpoints)"
	@echo "debug  - runs the application in debug mode (able to use pdb breakpoints)"
	@echo "clean  - WARNING: delete all containers, images and volumes on your system"

start:
	docker-compose -f docker-compose.dev.yml up

stop:
	docker-compose -f docker-compose.dev.yml down

test:
	docker-compose -f docker-compose.dev.yml run --rm --service-ports web pytest -s

debug:
	docker-compose -f docker-compose.dev.yml run --rm --service-ports web

clean:
	-docker rm `docker ps -aq`
	-docker rmi `docker images -aq`
	-docker volume rm `docker volume ls -q`
