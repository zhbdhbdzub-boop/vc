# Generated manually to create ConversationMessage table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0002_add_realtime_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversationMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(max_length=20, choices=[('interviewer', 'AI Interviewer'), ('candidate', 'User/Candidate'), ('system', 'System Message')])),
                ('content', models.TextField()),
                ('audio_url', models.URLField(blank=True)),
                ('duration_seconds', models.FloatField(default=0)),
                ('sentiment', models.CharField(max_length=20, blank=True)),
                ('confidence_score', models.IntegerField(default=0)),
                ('keywords_detected', models.JSONField(default=list, blank=True)),
                ('timestamp_seconds', models.FloatField(default=0)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation_messages', to='interviews.interviewsession')),
            ],
            options={
                'db_table': 'interviews_conversation_messages',
                'ordering': ['session', 'timestamp_seconds'],
            },
        ),
        migrations.AddIndex(
            model_name='conversationmessage',
            index=models.Index(fields=['session', 'timestamp_seconds'], name='interviews_session_idx'),
        ),
        migrations.AddIndex(
            model_name='conversationmessage',
            index=models.Index(fields=['role'], name='interviews_role_idx'),
        ),
    ]
