# Generated by Django 3.2 on 2021-09-15 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orakel', '0025_processstepspecification_machinelearningrun'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tool',
            name='processstep',
        ),
        migrations.AddField(
            model_name='tool',
            name='processstep',
            field=models.ManyToManyField(blank=True, default=None, null=True, related_name='tool', to='orakel.ProcessStep'),
        ),
    ]
