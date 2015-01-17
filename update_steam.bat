echo off
del data_shaymus22.py
copy steam_shaymus22.py data_shaymus22.py
python cheevos.py shaymus22
python cheevos_do.py shaymus22
python listTags.py shaymus22
del steam_shaymus22.py
copy data_shaymus22.py steam_shaymus22.py
REM python ratings_query.py shaymus22
REM python steam_ratings.py shaymus22
REM python ratings_query.py shaymus22
REM python ratings_analyze.py shaymus22
python steam_time.py
python steam_time_convert_to_js.py
echo on