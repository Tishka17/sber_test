## Задание

#### Сервис электронного кошелька. 

Из обязательного функционала только перевод денег между пользователями. 
Дополнительно условие: нельзя перевести пользователю деньги если на его счету больше чем N средств.

Достаточно работы сервиса из консоли без GUI клиента.

Предпочтительна реализация на чистом Python либо с минимальным использования фреймворков.

## Релизация

Так как в рамках задания не предполагается аутентификации в базе данных создается одна таблица, содержащя данные пользователя.

* `id` - суррогатный ключ
* `name` - естественный ключ (имя человека)
* Так же хранятся огранчиения на количество денег и текущее доступное количество.

![](http://www.plantuml.com/plantuml/png/SoWkIImgAStDuUBAJyfAJIvHA2rEBLAevb9Gi57BJgsqKyXCGR3p4dDJWRpSpBpunDpyqhmI42Un0i59BYqgIiqhWGdKSZcavgK0JGS0)


Выполнение огранчиений контролируется средствами БД.


## Использование

Для работы требуется Python 3.6

1. Установите зависимости (их мало):
    ```bash 
    pip3 install -r requirements.txt
    ```
2. Настройте параметры досутпа к базе данных Postgresql в файле `production.yml`. 
  При необходимости так же укажите параметры тестового сервера в `test.yml`
3. Инициализируйте БД с помощью скрипта `src/init.py`
4. Добавьте пользователей с помощью `src/add_user.py`. Например,
    ```bash
    ./src/add_user.py -n tishka17 --max 1000 -c 1
    ``` 
5. Переводите деньги с помощью скрипта `src/transfer.py` и смотрите текущее состояние с помощью `src/get.py`. Напрмиер,
    ```bash
    ./src/transfer.py -f tishka17 -t ivan -1
    ```


## Возможные доработки

### Аутентификация

Аутентификация и авторизация пользователей возможна с помощью одного из вариантов:
* Внешний сервер (LDAP)
* Таблица, содержащая хэши паролей

## Масштаблирование

Для масштабирования системы предлагается шардировать пользователей по серверам:

1. На одном сервере ведется таблица соответствия id пользователя и id шарда. 
2. При регистрации пользователя он сохраняется на одном из шардов
3. ПРи добавлении шарда на него могут быть перемещены некоторые существующие пользователи в фоновом режиме
4. При необходимости перевода денег 
    1. Определяются на каких шардах находятся пользвоатели
    2. Если они в прежелах одного шарда, вызывается алгоритм обычного перевода денег в одной транзакции
    3. Если пользователи раположены на разных шардах, используются распределенных транзакции (2PC или 3PC)