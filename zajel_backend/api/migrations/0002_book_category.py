# Generated by Django 5.2.4 on 2025-07-05 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.CharField(choices=[('روايات', 'روايات'), ('تاريخ', 'تاريخ'), ('علوم', 'علوم'), ('فلسفة', 'فلسفة'), ('أدب', 'أدب'), ('دين', 'دين')], default='روايات', max_length=50),
        ),
    ]
