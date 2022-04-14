# Generated by Django 3.2 on 2021-07-28 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orakel', '0021_alter_dataframe_max_rows'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataframe',
            old_name='max_rows',
            new_name='product_amount',
        ),
        migrations.RemoveField(
            model_name='dataframe',
            name='processparameter_choice',
        ),
        migrations.RemoveField(
            model_name='dataframe',
            name='processstepspecification_choice',
        ),
        migrations.RemoveField(
            model_name='dataframe',
            name='qualitycharacteristics_choice',
        ),
        migrations.AddField(
            model_name='dataframe',
            name='feature_config',
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
