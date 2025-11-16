# Generated manually to add real-time interview fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0001_initial'),
    ]

    operations = [
        # Add new fields to InterviewSession if they don't exist
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Add job_role if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'job_role'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN job_role VARCHAR(255) DEFAULT '';
                END IF;
                
                -- Add company_name if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'company_name'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN company_name VARCHAR(255) DEFAULT '';
                END IF;
                
                -- Add mode if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'mode'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN mode VARCHAR(20) DEFAULT 'practice';
                END IF;
                
                -- Add interviewer_avatar_url if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'interviewer_avatar_url'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN interviewer_avatar_url VARCHAR(200) DEFAULT '';
                END IF;
                
                -- Add transcript if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'transcript'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN transcript TEXT DEFAULT '';
                END IF;
                
                -- Add response_times if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'response_times'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN response_times JSONB DEFAULT '[]';
                END IF;
                
                -- Add filler_words_count if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'filler_words_count'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN filler_words_count INTEGER DEFAULT 0;
                END IF;
                
                -- Add speaking_pace if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'speaking_pace'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN speaking_pace VARCHAR(20) DEFAULT '';
                END IF;
                
                -- Add problem_solving_score if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'interviews_sessions' AND column_name = 'problem_solving_score'
                ) THEN
                    ALTER TABLE interviews_sessions ADD COLUMN problem_solving_score INTEGER DEFAULT 0;
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE interviews_sessions 
                DROP COLUMN IF EXISTS job_role,
                DROP COLUMN IF EXISTS company_name,
                DROP COLUMN IF EXISTS mode,
                DROP COLUMN IF EXISTS interviewer_avatar_url,
                DROP COLUMN IF EXISTS transcript,
                DROP COLUMN IF EXISTS response_times,
                DROP COLUMN IF EXISTS filler_words_count,
                DROP COLUMN IF EXISTS speaking_pace,
                DROP COLUMN IF EXISTS problem_solving_score;
            """
        ),
    ]
