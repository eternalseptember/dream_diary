# Dream Diary

Forked from [this project](https://github.com/eternalseptember/rpi-test), this is the "live" version that is hosted on my raspberry pi for personal use.

## Problems That Were Fixed

### The Symbols were alphabetized correctly on my raspberry pi, but not on my WSL-Ubuntu?

Symbols that begin with capital letters sort differently than lowercased letters. How was this not found when I was going through [this](https://github.com/eternalseptember/rpi-test)? Because none of my test tags in that test project used capital letters.

The issue is on the postgres level, where I had to create a custom collation to get words to sort case-insensitively...
```
CREATE COLLATION case_insensitive (
  provider = icu, 
  locale = 'en-US-u-ks-level2',
  deterministic = false);
```

because postgres does not support database-wide, non-deterministic (i.e. because we want capital 'A' to be equal to lowercase 'a', and deterministic sorting involves byte-wise comparisons that will respect that capital 'A' and lowercase 'a' are two different things) collation until like... version 17 or something? (I'm on version 15.) I didn't even need database-wide, case-insensitive collation; I just needed it on the symbols field.

Couldn't I just
"""
ALTER TABLE public.dreams_symbol ALTER COLUMN name TYPE varchar(255) COLLATE case_insensitive;
"""

? No. It told me:

> nondeterministic collations are not supported for operator class "varchar_pattern_ops"


My struggle wasn't on how to sort this field alphabetically from like, psql or pgAdmin:
```
SELECT * FROM public.dreams_symbol 
ORDER BY name 
COLLATE case_insensitive DESC;
```

but how to do it in django??? To make that field sort alphabetically in the admin panel? How does django interface with the sql?

[Credit to this guy](https://adamj.eu/tech/2023/02/23/migrate-django-postgresql-ci-fields-case-insensitive-collation/)

1. `python manage.py makemigrations <app_name> --empty --name case_insensitive_collation` which resulted in the file `dreams/migrations/0002_case_insensitive_collation.py`,

2. which was edited to this:

```
# Generated by Django 5.1.4 on 2025-01-26 07:55
from django.contrib.postgres.operations import CreateCollation
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dreams', '0001_initial'),
    ]

    operations = [
        CreateCollation(
            "case_insensitive",
            provider="icu", 
            locale="en-US-u-ks-level2", 
            deterministic=False
            ),
    ]
```

3. ran `python manage.py sqlmigrate <app_name> 0002`, which appeared to have no errors.
4. Then added `db_collation="case_insensitive"` to the symbol model name, then
5. `python manage.py makemigrations`
6. `python manage.py sqlmigrate <app_name> 0003`
7. `python manage.py migrate`

Naturally, this all runs fine on WSL-Ubuntu without errors, but on the raspberry pi, which was sorting things case-insensitively in the first place, there was an error at at step 7:

> nondeterministic collations are not supported for operator class "varchar_pattern_ops"

which is the same error I had on WSL-Ubuntu when I tried to alter the column directly through pgAdmin.
