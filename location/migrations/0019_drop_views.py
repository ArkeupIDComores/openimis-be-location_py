from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0018_auto_20230925_2243'),
    ]

    operations = [
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwAmountRejected";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwAmountClaimed";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwAmountValuated";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwClaimEntered";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwClaimProcessed";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwClaimRejected";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwClaimSent";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwClaimSubmitted";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwClaimValuated";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwHospitalAdmissions";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwHospitalDays";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwAmountApproved";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwNumberFeedbackAnswerYes";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwNumberFeedbackResponded";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwNumberFeedbackSent";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwOverallAssessment";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwVisit";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwItemUtilization";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwServiceUtilization";'
        ),
        migrations.RunSQL(
            'DROP VIEW IF EXISTS "public"."uvwItemExpenditures";'
        ),
    ]