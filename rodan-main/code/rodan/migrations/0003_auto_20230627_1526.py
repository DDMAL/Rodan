from django.db import migrations, models
import rodan.models.user


class Migration(migrations.Migration):
    """
    This migration makes the email field unique and non-blank.
    """

    dependencies = [
        ('rodan', '0002_auto_20230522_1420'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', rodan.models.user.UserManager()),
            ],
        ),
        # Make sure there are no empty email fields by giving them a default value
        migrations.RunSQL(
            sql="UPDATE auth_user SET email = CONCAT(username, '@rodan2.simssa.ca') WHERE email = ''",
            reverse_sql="UPDATE auth_user SET email = '' WHERE email LIKE '%@rodan2.simssa.ca'"
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
