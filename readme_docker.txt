Шаг 1: Надо создать своего юзера в хостинге
        - В карточке KGF-7 есть комментарий инструкция "Начальный этап". Полностью все шаги как там, только следующие параметры поменяйте:
            IP-adress: 146.185.146.5
            root password: kGs4YzdFtBeIEfCrAgM7HUDqhvuNy9wW
            new user: везде где прописано "dastan" пропишите свое имя

Шаг 2: клонирование проекта:
        - когда войдете со своим ssh ключом (например: ssh dastan@146.185.146.5), вы сразу попадете на свою домашнюю папку.
          В терминале ваша строка будет начинаться на ~. А обсолютный путь к вашей папке будет выглядеть так: /home/dastan/ или /home/akram/
        - в эту папку склонируйте наш проект из гита. В итоге у вас должно получится: /home/dastan/kyrgyz_go_database.
            Т.е. находясь в своей домашней директории если наберете команду ls, то увидите папку нашего проекта.
            Если будут трудности с клонированием проекта, посмотрите комментарий "Инструкция для клонирования на сервер" - третий комментарий с низу.
        - стянитесь до актуальной версии дева

Шаг 3: Запуск проекта через докер:
        - войдите в папку проекта. Вы должны оказаться в ~/kyrgyz_go_database (/home/artur/kyrgyz_go_database)
        - docker-compose up -d --build  # это может занять много времени, образ приложения получился почти на гигабайт.
            Данная команда загрузит образы и запустит контейнера по ним. Успешное выполнение данной команды в нашем случае покажет три
            строки с зелеными "done", так как у нас три образа.
        - docker-compose ps  # эта команда покажет активные контейнера.
        - теперь надо прогнать миграции командой: docker-compose exec web python3 manage.py migrate  ## почему-то у меня manage.py работает через python3
        - а теперь собрать статики: docker-compose exec web python3 manage.py collectstatic
        - создать супер юзера: docker-compose exec web python3 manage.py createsuperuser
        - зарегать job`ы: docker-compose exec web python3 manage.py runapscheduler
        - загрузить данные из фикстур:
        	- docker-compose exec web python3 manage.py loaddata fixtures/partner.json
        	- docker-compose exec web python3 manage.py loaddata fixtures/days.json
         Да в принципе все и готово.



Шаг 4(доп.): Если надо обновить код (git pull):
        - просто зайдите в папку проекта - kyrgyz_go_database
        - cтяните актуальную версию
        - выполните следующую команду для остановки контейнеров: docker-compose down
        - если хотите удалить все записи из базы данных, статики и медиа; дополните команду выше флажком -v: docker-compose down -v
            так вы очистите volumes
        - а теперь обратно поднимите проект: docker-compose up -d --build
        - проганите миграции: docker-compose exec web python3 manage.py migrate
        - зарегать job`ы: docker-compose exec web python3 manage.py runapscheduler
        - если удаляли volumes, то соберите обратно статики. А записи в бд потеряны если только у вас нет фикстур.
            Загрузите фикстуры и ваш сайт готов.





Основные команды:
    - docker-compose up -d --build
    - docker-compose down [или docker-compose down -v]

    - docker-compose exec web python3 manage.py migrate  ## exec отркывает контейнер.
        В этой команде открывается контейнер web (у нас еще есть контейнеры "db" и "nginx", если взглянете в файл docker-compose.yml)


Второстепенные команды:
    - docker-compos ps [или docker ps]  ## показывает список активных контейров
    - docker-compose ps -a  ## с флажком -a можно посмотреть все контейнеры, включая неактивные.

    - docker-compose exec web bash  ##заходит в контейнер, где можно писать bash srcipt в командной строке контейнера
    - docker-compose exec nginx sh   ##когда bash не срабатывает.
    - docker-compose exec db psql --username=admin --dbname=kgf  ##так вы можете отркыть shell postgres и писать sql запросы
        командная строка должна у вас начинаться на: kgf=#
            kgf=# \l   --> покажет список баз данных
            kgf=# \dt   --> покажет таблицы
            kgf=# \q   --> чтоб выйти
            \c kgf или \connect kgf   --> чтоб подключится к нашей базе




Примечания:
    - команды "docker" и "docker-compose" будут срабатывать, потому что я их уже установил через рут в хостинге.
        На новой машине, в будущем вам надо будет их для начала установить.
    - после того как создадите свою учетку на хостинге и склонируете проект, шаги 1 и 2 в последующем уже не понадобятся.
        т.е. их надо выполнить только один раз

