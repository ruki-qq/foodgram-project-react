# Generated by Django 4.2.10 on 2024-03-20 02:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_alter_user_followers"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="followrelationship",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Подписка",
                "verbose_name_plural": "Подписка",
            },
        ),
        migrations.AddField(
            model_name="followrelationship",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата создания",
            ),
            preserve_default=False,
        ),
    ]
