# report_generator
Your report generator system: upload, view, download


## Требования
Создайте приложение, которое принимает через форму файл формата .csv и возвращает на страницу после загрузки формы отчет, содержащий данные по образцу отчета. На странице должна быть кнопка «скачать», при нажатии на которую скачивается отчет в формате .docx. 


## Реализация
- [x] Форма для приёма файла
- [x] Вью для логики
- [x] Настройки
- [x] Шаблон
- [x] Документация

Настройки для отчёта вынесены в settings в раздел REPORT_CONFIG:
- fields_to_display - поля для отображения 
- sum_fields - поля для вычисления суммы
- required_field - обязательные поля, без заполнения которых строка не будет выходить в отчёт
- field_mappings - мапинг полей в csv и названиями в отчёте
- number_format - форматирование чисел
- unit_divisors - преобразование ед.изм.

## Технологии
Python 3.9, Django, python-docx
Все требования к установке описаны в report_generator/requirements.txt

## Запуск проекта
Для запуска проекта выполните последовательно команды:

```bash
git clone https://github.com/belyashnikovatn/report_generator
```

```bash
python -m venv venv   
. venv/Scripts/activate  
python -m pip install --upgrade pip  
pip install -r requirements.txt   
cd report_project/
python manage.py migrate   
python manage.py runserver   
```

Перейдите по ссылке:  
http://127.0.0.1:8000/  
Откроется домашняя страница
