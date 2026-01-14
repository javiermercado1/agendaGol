.PHONY: init start stop logs status clean

init:
	docker-compose up --build

start:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

status:
	docker-compose ps

clean:
	docker-compose down -v
	rm -f *.db auth_service/*.db roles_service/*.db fields_service/*.db reservations_service/*.db
