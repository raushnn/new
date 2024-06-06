# Generated by Django 5.0 on 2023-12-14 14:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ai", "0018_alter_document_embedding_status"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="available_documents",
            field=models.ManyToManyField(
                blank=True,
                related_name="available_for",
                to="ai.document",
                verbose_name="Доступные документы",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="has_full_access",
            field=models.BooleanField(default=False, verbose_name="Полный доступ ?"),
        ),
    ]