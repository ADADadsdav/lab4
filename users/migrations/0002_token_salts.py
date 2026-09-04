from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('users', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='usertoken', name='token_salt',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='passwordresettoken', name='token_salt',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
