# Generated by Django 4.2.13 on 2024-05-08 12:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Analysis",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("boxes_count", models.IntegerField()),
                ("score_threshold", models.FloatField()),
                ("image_height", models.IntegerField()),
                ("image_width", models.IntegerField()),
                ("timestamp", models.DateTimeField(auto_now=True)),
                ("original_file_path", models.CharField(max_length=1000)),
                ("result_file_path", models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="DetectedAnimal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.FloatField()),
                ("breed", models.CharField(max_length=100)),
                ("species", models.CharField(max_length=100)),
                ("start_x", models.FloatField()),
                ("start_y", models.FloatField()),
                ("end_x", models.FloatField()),
                ("end_y", models.FloatField()),
                (
                    "analysis",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="animals.analysis",
                    ),
                ),
            ],
        ),
    ]
