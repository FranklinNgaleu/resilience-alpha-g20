.RECIPEPREFIX = >
.PHONY: up down reset restore check ps logs

# Par défaut : Ansible dans un conteneur (scripts/ansible.sh).
# Pour utiliser Ansible installé dans Ubuntu :
#   make up ANSIBLE='ansible-playbook -i infra/ansible/inventory.ini'
ANSIBLE ?= ./scripts/ansible.sh

up:
> $(ANSIBLE) infra/ansible/deploy.yml

down:
> docker compose down

reset:
> $(ANSIBLE) infra/ansible/reset.yml

restore:
> $(ANSIBLE) infra/ansible/restore.yml

ps:
> docker compose ps

logs:
> docker compose logs -f --tail=100

check:
> ./scripts/precheck.sh
