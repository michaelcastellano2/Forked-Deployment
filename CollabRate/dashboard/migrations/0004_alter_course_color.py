# Generated by Django 5.1.4 on 2025-03-14 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_alter_course_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='color',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
