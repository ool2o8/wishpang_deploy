# Generated by Django 4.0.5 on 2022-07-03 18:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(help_text='Post ID', primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Post title', max_length=100)),
                ('contents', models.TextField(help_text='post contents')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(help_text='Comment ID', primary_key=True, serialize=False)),
                ('contents', models.TextField(help_text='Comment contents')),
                ('post_id', models.ForeignKey(db_column='post_id', on_delete=django.db.models.deletion.CASCADE, related_name='post', to='blog.post')),
            ],
        ),
    ]
