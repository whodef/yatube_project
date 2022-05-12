# Generated by Django 2.2.6 on 2022-05-12 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20220329_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Выберите группу для новой записи', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Добавьте текст для новой записи', verbose_name='Текст'),
        ),
    ]
