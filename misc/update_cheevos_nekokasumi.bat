echo off
del data_nekokasumi.py
copy steam_nekokasumi.py data_nekokasumi.py
python cheevos.py nekokasumi
python cheevos_do.py nekokasumi
python listTags.py nekokasumi
del steam_nekokasumi.py
copy data_nekokasumi.py steam_nekokasumi.py
python ratings_query.py nekokasumi
python steam_ratings.py nekokasumi
python ratings_query.py nekokasumi
python ratings_analyze.py nekokasumi
echo on