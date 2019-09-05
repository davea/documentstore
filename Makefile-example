run:
	pipenv run honcho start

clean:
	pipenv --rm

clean_pipfile:
	rm Pipfile.lock

update_pipfile: clean clean_pipfile pipenv

pipenv:
	pipenv install
	pipenv install -d

requirements:
	pipenv run pipenv_to_requirements -f

db:
	dropdb documentstore || true
	createdb documentstore
	ssh documentstore pg_dump -h database -U documentstore -d documentstore -O | psql documentstore

media_root:
	rsync -r --progress documentstore:/mnt/documentstore/ ~/Code/documentstore/media_root/

sync: db media_root
