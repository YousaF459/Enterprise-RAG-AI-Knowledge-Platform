from django.db import migrations
from django.contrib.postgres.operations import CreateExtension
import pgvector.django.vector


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_documentchunk'),
    ]

    operations = [
        CreateExtension("vector"),

        migrations.AddField(
            model_name='documentchunk',
            name='embedding',
            field=pgvector.django.vector.VectorField(
                blank=True,
                dimensions=384,
                null=True,
            ),
        ),
    ]