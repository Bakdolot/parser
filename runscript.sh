#!/bin/bash
echo "start" >> /home/mylog.log

/home/parser/venv/bin/python /home/parser/parser.py RENT_GARAGE
/home/parser/venv/bin/python /home/parser/parser.py DAILY_RENT_APARTMENT
/home/parser/venv/bin/python /home/parser/parser.py LONG_TERM_RENT_APARTMENT
/home/parser/venv/bin/python /home/parser/parser.py SALE_GARAGE
/home/parser/venv/bin/python /home/parser/parser.py DAILY_RENT_HOUSE
/home/parser/venv/bin/python /home/parser/parser.py LONG_TERM_RENT_HOUSE
/home/parser/venv/bin/python /home/parser/parser.py SALE_HOUSE
/home/parser/venv/bin/python /home/parser/parser.py SALE_APARTMENT
/home/parser/venv/bin/python /home/parser/parser.py SALE_SECTION
/home/parser/venv/bin/python /home/parser/parser.py RENT_SECTION
echo "end\n" >> /home/mylog.log
