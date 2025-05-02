# Ansible — ВОТ Домашно

Показвам Ansible playbook, който автоматично:

- Обновява списъка с пакети
- Инсталира полезни програми (`htop`, `curl`, `neofetch`)
- Създава файл `/tmp/WELCOME.txt` с текст
- Променя hostname-а на машината

## Как работи

### Инсталирам Ansible (ако не е инсталиран):

```
sudo apt update
sudo apt install ansible -y```
Файлове в проекта:
```

`hosts.ini`: inventory файл с информация за машината (localhost)

`playbook.yml`: playbook с задачите за автоматизация

### Стартираме playbook-а с команда:

```ansible-playbook -i hosts.ini playbook.yml --ask-become-pass```

`--ask-become-pass` казва на Ansible да използва sudo, като поиска парола.

### Oчакван резултат:

Инсталират се пакети

Създава се файл /tmp/WELCOME.txt с текст

Променя hostname-а на @vot-ansible-demo

### Връщаме предишния hostname (yasens-Precision-5680) с:

```ansible-playbook -i hosts.ini reset-playbook.yml --ask-become-pass```

