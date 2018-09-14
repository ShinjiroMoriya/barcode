#実行時「make -j」
.PHONY: all
.PHONY: server
.PHONY: sass
.PHONY: sass-min
.PHONY: webpack
.PHONY: pep8
.PHONY: redis
.PHONY: jsmin
.PHONY: freeze


scssFromPath = resources/scss/
scssToPath   = assets/css/
scssCombPath = resources/scss/

all: sass

server:
	python manage.py runsslserver --key localhost.key --certificate localhost.crt

freeze:
	pip freeze > requirements.txt

jsmin:
	python feed_app/jsmin.py

jswatch:
	watchmedo shell-command --patterns="*.js" --recursive --command='make jsmin' 'resources/'

radis:
	redis-server

sass:
	sass --sourcemap=none --no-cache --watch $(scssFromPath):$(scssToPath) --style compressed

csscomb:
	csscomb ${scssCombPath}

pep8: ## pep8フォーマットに変換
	@pep8 . | cut -d: -f 1 | sort | uniq | xargs autopep8 -i

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
