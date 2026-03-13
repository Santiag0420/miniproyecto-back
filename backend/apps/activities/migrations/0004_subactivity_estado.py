from django.db import migrations, models


def completada_a_estado(apps, schema_editor):
    SubActivity = apps.get_model('activities', 'SubActivity')
    SubActivity.objects.filter(completada=True).update(estado='hecha')
    SubActivity.objects.filter(completada=False).update(estado='pendiente')


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_alter_activity_curso'),
    ]

    operations = [
        migrations.AddField(
            model_name='subactivity',
            name='estado',
            field=models.CharField(
                choices=[('pendiente', 'Pendiente'), ('hecha', 'Hecha'), ('pospuesta', 'Pospuesta')],
                default='pendiente',
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name='subactivity',
            name='nota_posposicion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(completada_a_estado, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='subactivity',
            name='completada',
        ),
    ]
