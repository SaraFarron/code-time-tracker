# Generated by Django 5.0.2 on 2024-02-11 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wakatime_data', '0002_alter_wakatimedata_digital'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wakatimedata',
            name='percent',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='percent'),
        ),
    ]
