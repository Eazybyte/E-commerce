# Generated by Django 4.1.4 on 2022-12-26 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_product_variations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='variations',
        ),
        migrations.AddField(
            model_name='variation',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
    ]
