pybabel extract --input-dirs=. -o locales/time_tracker.pot
pybabel init -i locales/time_tracker.pot -d locales -D time_tracker -l en
pybabel init -i locales/time_tracker.pot -d locales -D time_tracker -l ru
