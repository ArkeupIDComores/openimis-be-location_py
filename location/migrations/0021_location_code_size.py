from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0020_hfcode_create_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='code',
            field=models.CharField(db_column='LocationCode', max_length=50),
        )
    ]