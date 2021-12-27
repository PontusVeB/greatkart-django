# Generated by Django 3.1 on 2021-12-22 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
        ('orders', '0003_auto_20211221_2112'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='variation',
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='product_variations',
            field=models.ManyToManyField(blank=True, to='store.Variation'),
        ),
    ]
