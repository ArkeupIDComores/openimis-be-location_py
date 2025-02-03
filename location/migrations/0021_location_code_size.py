from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0020_hfcode_create_views'),
    ]

    operations = [

        migrations.RunSQL(
            """
            -- Delete View first
            DROP VIEW IF EXISTS public."tblDistricts";
            DROP VIEW IF EXISTS public."tblRegions";
            DROP VIEW IF EXISTS public."tblVillages";
            DROP VIEW IF EXISTS public."tblWards";
            """
        ),
        migrations.AlterField(
            model_name='location',
            name='code',
            field=models.CharField(db_column='LocationCode', max_length=50),
        ),
        migrations.RunSQL(
            """
            -- Recreate View
            CREATE OR REPLACE VIEW public."tblDistricts"
            AS
            SELECT "tblLocations"."LocationId" AS "DistrictId",
                "tblLocations"."LocationCode" AS "DistrictCode",
                "tblLocations"."LocationName" AS "DistrictName",
                "tblLocations"."ParentLocationId" AS "Region",
                "tblLocations"."ValidityFrom",
                "tblLocations"."ValidityTo",
                "tblLocations"."LegacyID",
                "tblLocations"."AuditUserId",
                "tblLocations"."RowId"
            FROM "tblLocations"
            WHERE "tblLocations"."ValidityTo" IS NULL AND "tblLocations"."LocationType"::bpchar = 'D'::bpchar;

            CREATE OR REPLACE VIEW public."tblRegions"
            AS
            SELECT "tblLocations"."LocationId" AS "RegionId",
                "tblLocations"."LocationCode" AS "RegionCode",
                "tblLocations"."LocationName" AS "RegionName",
                "tblLocations"."ValidityFrom",
                "tblLocations"."ValidityTo",
                "tblLocations"."LegacyID",
                "tblLocations"."AuditUserId",
                "tblLocations"."RowId"
            FROM "tblLocations"
            WHERE "tblLocations"."ValidityTo" IS NULL AND "tblLocations"."LocationType"::bpchar = 'R'::bpchar;

            CREATE OR REPLACE VIEW public."tblVillages"
            AS
            SELECT "tblLocations"."LocationId" AS "VillageId",
                "tblLocations"."ParentLocationId" AS "WardId",
                "tblLocations"."LocationCode" AS "VillageCode",
                "tblLocations"."LocationName" AS "VillageName",
                "tblLocations"."MalePopulation",
                "tblLocations"."FemalePopulation",
                "tblLocations"."OtherPopulation",
                "tblLocations"."Families",
                "tblLocations"."ValidityFrom",
                "tblLocations"."ValidityTo",
                "tblLocations"."LegacyID",
                "tblLocations"."AuditUserId"
            FROM "tblLocations"
            WHERE "tblLocations"."ValidityTo" IS NULL AND "tblLocations"."LocationType"::bpchar = 'V'::bpchar;

            CREATE OR REPLACE VIEW public."tblWards"
            AS
            SELECT "tblLocations"."LocationId" AS "WardId",
                "tblLocations"."ParentLocationId" AS "DistrictId",
                "tblLocations"."LocationCode" AS "WardCode",
                "tblLocations"."LocationName" AS "WardName",
                "tblLocations"."ValidityFrom",
                "tblLocations"."ValidityTo",
                "tblLocations"."LegacyID",
                "tblLocations"."AuditUserId"
            FROM "tblLocations"
            WHERE "tblLocations"."ValidityTo" IS NULL AND "tblLocations"."LocationType"::bpchar = 'W'::bpchar;


            """
        ),
    ]