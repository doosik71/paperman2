# Generated by Django 5.1.7 on 2025-03-24 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("paper", "0006_paper_abstract"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paper",
            name="citations",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
