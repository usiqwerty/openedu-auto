# openedu-auto
Автоматический решатель тестов для OpenEdu

## Установка и запуск
Тестировалось на Python 3.12

Процесс установки без каких-либо особенностей:
```shell
git clone https://github.com/usiqwerty/openedu-auto.git
cd openedu-auto
pip install -r requirements.txt
```

Далее запускаем:
```shell
python main.py
```

При первом запуске нужно будет ввести данные для авторизации.
Это в точности те же самые данные, которые вы вводите при входе на Openedu.


## Решение в файле
В папке `userdata/solutions` можно положить JSON файлы с решениями.

Чтобы их использовать нужно выбрать в меню `решение из файла`
и вставить ссылку на курс.

Выглядеть это будет примерно так:
```
$ python main.py
1. Решить через нейросеть
2. Решить из файла
3. Сохранить решение в файл
4. Сбросить куки
5. Сбросить кеш
Ввод: 2
Вставьте ссылку на курс. Она может иметь следующий вид:
1) https://openedu.ru/course/urfu/HIST/?session=spring_2025
2) https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/home
Ссылка: https://openedu.ru/course/urfu/HIST/?session=spring_2025
Будем решать курс История России
Нажимте Enter, чтобы начать, иначе выйдем 
```

## Документация
[Для разрабов](docs/dev.md)