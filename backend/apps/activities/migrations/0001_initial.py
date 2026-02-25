from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[
                        ('exam', 'Examen'),
                        ('quiz', 'Quiz'),
                        ('workshop', 'Taller'),
                        ('project', 'Proyecto'),
                        ('other', 'Otro'),
                    ],
                    default='other',
                    max_length=20,
                )),
                ('titulo', models.CharField(max_length=255)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('curso', models.CharField(max_length=255)),
                ('fecha_evento', models.DateTimeField(blank=True, null=True)),
                ('fecha_limite', models.DateField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='activities',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.CreateModel(
            name='SubActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('fecha_objetivo', models.DateField()),
                ('horas_estimadas', models.DecimalField(decimal_places=1, max_digits=5)),
                ('completada', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subactivities',
                    to='activities.activity',
                )),
            ],
        ),
    ]
