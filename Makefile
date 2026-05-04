.PHONY: test lint tox commit copy

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .

tox:
	uv run tox

ci: lint test
	echo "✅ CI пройден"

commit:
	@read -p "Введите сообщение коммита: " msg; \
	git add -A; \
	git commit -m "$$msg | added via Makefile"; \
	git push

copy:
	bash bin/!copyTreeProject.bash

view-full:
	bash bin/!toggle_bash_view.bash <<< "y"

view-clean:
	bash bin/!toggle_bash_view.bash <<< "n"

view-full:
	@echo "y" | bash bin/!toggle_bash_view.bash

view-clean:
	@echo "n" | bash bin/!toggle_bash_view.bash

view-full:
	@echo "y" | bash bin/!toggle_bash_view.bash

view-clean:
	@echo "n" | bash bin/!toggle_bash_view.bash
