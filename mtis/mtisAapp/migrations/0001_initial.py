# Generated by Django 4.2.6 on 2024-03-19 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('type', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='EntryGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(default=1)),
                ('main', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='main_entrygroup', to='mtisAapp.entry')),
                ('root', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='root_entrygroup', to='mtisAapp.entry')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('a', models.TextField()),
                ('b', models.TextField()),
                ('nextQa', models.IntegerField(null=True)),
                ('nextQb', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Weights',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Xfactor', models.FloatField(default=0.0)),
                ('Yfactor', models.FloatField(default=0.0)),
                ('Zfactor', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chapter0', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mtisAapp.question')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='weights',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mtisAapp.weights'),
        ),
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mtisAapp.entry')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mtisAapp.entrygroup')),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challenger_challenge', to='mtisAapp.entry')),
                ('in_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_question_challenge', to='mtisAapp.entry')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
                ('netAB', models.IntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mtisAapp.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mtisAapp.user')),
            ],
        ),
    ]
