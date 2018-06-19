# ДетскоеТВ

Проект для запуска мультиков детям в строго отведённое время и в лимитированном количестве.

Подразумевается запуск на Raspberry Pi подключённой к телевизору. Мультики играют с флешки.

Между проигрыванием показывается веб-страница с часами и расписанием сколько до следующего мультика.

## Getting Started

Всё что потребуется — ssh подключение к Raspberry Pi и немного терпения


### Prerequisites

На Raspberry должен быть установлен nginx:

https://www.raspberrypi.org/documentation/remote-access/web-server/nginx.md

Инструкция по запуск полноэкранного браузера при старте Raspberry:

https://blog.gordonturner.com/2017/07/22/raspberry-pi-full-screen-browser-raspbian-july-2017/


### Installing

### Скачиваем репозиторий в домашнюю папку user'а `pi`

```
cd /home/pi
git clone git@github.com:romanesko/vplayer.git

```


### Настройки

Отредактируйте файл /home/pi/config.json указав папки с мультфильмами

NB! Мультфильмы в папке UNWATCHED должны находиться в папках одного уровня. 

Например:

/usb/unwatched/щенячий патруль/..
/usb/unwatched/ну погоди/..


### Добавляем в `cron` расписание запуска


```
crontab -l > ./mycron
echo "0 9 * * * /home/pi/vplayer.py" >> ./mycron
echo "0 21 * * * /home/pi/vplayer.py" >> ./mycron
crontab ./mycron
rm ./mycron

```


