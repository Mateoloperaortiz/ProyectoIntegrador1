from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='favoriteprompt',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
        migrations.AddField(
            model_name='sharedchat',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated at'),
        ),
    ]