echo off
del data_nekokasumi.py
copy steam_nekokasumi.py data_nekokasumi.py
python cheevos.py nekokasumi
python cheevos_do.py nekokasumi
python listTags.py nekokasumi
del steam_nekokasumi.py
copy data_nekokasumi.py steam_nekokasumi.py
REM python ratings_query.py nekokasumi
REM python steam_ratings.py nekokasumi
REM python ratings_query.py nekokasumi
REM python ratings_analyze.py nekokasumi


REM python steam_time.py
REM python steam_time_convert_to_js.py
echo on