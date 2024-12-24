from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0019_drop_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthfacility',
            name='code',
            field=models.CharField(db_column='HFCode', max_length=50),
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwAmountRejected" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwAmountRejected" AS
            SELECT 
                SUM("Details"."Rejected") AS "amountrejected",
                MONTH(COALESCE("C"."DateTo", "C"."DateFrom")) AS "MonthTime",
                QUARTER(COALESCE("C"."DateTo", "C"."DateFrom")) AS "QuarterTime",
                YEAR(COALESCE("C"."DateTo", "C"."DateFrom")) AS "YearTime",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" AS "C" 
            LEFT OUTER JOIN (
                SELECT 
                    "ClaimID", 
                    "ProdID", 
                    SUM("QtyProvided" * "PriceAsked") AS "Rejected"
                FROM "tblClaimItems" 
                WHERE "ValidityTo" IS NULL 
                GROUP BY "ClaimID", "ProdID"

                UNION ALL

                SELECT 
                    "ClaimID", 
                    "ProdID", 
                    SUM("QtyProvided" * "PriceAsked") AS "Rejected"
                FROM "tblClaimServices" 
                WHERE "ValidityTo" IS NULL 
                GROUP BY "ClaimID", "ProdID"
            ) AS "Details" ON "C"."ClaimID" = "Details"."ClaimID"

            LEFT OUTER JOIN "tblProduct" AS "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
            LEFT OUTER JOIN "tblHF" AS "HF" ON "C"."HFID" = "HF"."HfID"
            LEFT OUTER JOIN "tblDistricts" AS "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
            LEFT OUTER JOIN "tblRegions" AS "HFR" ON "HFR"."RegionId" = "HFD"."Region"

            WHERE 
                "C"."ValidityTo" IS NULL
                AND "Prod"."ValidityTo" IS NULL
                AND "HF"."ValidityTo" IS NULL
                AND "HFD"."ValidityTo" IS NULL
                AND "C"."ClaimStatus" = 1 -- Rejected claims only

            GROUP BY 
                MONTH(COALESCE("C"."DateTo", "C"."DateFrom")),
                QUARTER(COALESCE("C"."DateTo", "C"."DateFrom")),
                YEAR(COALESCE("C"."DateTo", "C"."DateFrom")),
                "HF"."HFLevel", 
                "HF"."HFCode", 
                "HF"."HFName",
                "Prod"."ProductCode", 
                "Prod"."ProductName",
                "HFD"."DistrictName", 
                "HFR"."RegionName";
            """
        ),

        migrations.RunSQL(
            """
            -- Recrée la vue "uvwAmountClaimed" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwAmountClaimed" AS
            SELECT SUM("Details"."Claimed") "AmountClaimed",
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "HFR"."RegionName" "Region", "HFD"."DistrictName",
                "Prod"."ProductCode", "Prod"."ProductName",
                "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
            FROM "tblClaim" "C" 
            LEFT OUTER JOIN (
                SELECT "ClaimID", "ProdID", SUM("QtyProvided" * "PriceAsked") "Claimed"
                FROM "tblClaimItems" 
                WHERE "ValidityTo" IS NULL 
                GROUP BY "ClaimID", "ProdID"
                UNION ALL
                SELECT "ClaimID", "ProdID", SUM("QtyProvided" * "PriceAsked") "Claimed"
                FROM "tblClaimServices" 
                WHERE "ValidityTo" IS NULL 
                GROUP BY "ClaimID", "ProdID"
            ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
            LEFT OUTER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
            LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
            LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
            LEFT OUTER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL
            AND "C"."ClaimStatus" <> 2 -- Exclude entered claims
            GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")), 
                    QUARTER(coalesce("C"."DateTo", "C"."DateFrom")), 
                    YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                    "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                    "Prod"."ProductCode", "Prod"."ProductName",
                    "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwAmountValuated" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwAmountValuated" AS
            SELECT SUM("Details"."Valuated") "AmountValuated",
                MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "HFR"."RegionName" "Region", "HFD"."DistrictName",
                "Prod"."ProductCode", "Prod"."ProductName",
                "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
            FROM "tblClaim" "C" 
            LEFT OUTER JOIN (
                SELECT "ClaimID", "ProdID", SUM("RemuneratedAmount") "Valuated"
                FROM "tblClaimItems" 
                WHERE "ValidityTo" IS NULL 
                GROUP BY "ClaimID", "ProdID"
                UNION ALL
                SELECT "ClaimID", "ProdID", SUM("RemuneratedAmount") "Valuated"
                FROM "tblClaimServices" 
                WHERE "ValidityTo" IS NULL 
                GROUP BY "ClaimID", "ProdID"
            ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
            LEFT OUTER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
            LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
            LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
            LEFT OUTER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL
            AND "C"."ClaimStatus" = 16 -- Processed claims
            GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")), 
                    QUARTER(coalesce("C"."DateTo", "C"."DateFrom")), 
                    YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                    "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                    "Prod"."ProductCode", "Prod"."ProductName",
                    "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwClaimEntered" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwClaimEntered" AS
        SELECT COUNT(1) "TotalClaimEntered",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
        WHERE "C"."ValidityTo" IS NULL
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwClaimProcessed" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwClaimProcessed" AS
        SELECT COUNT(1) "TotalClaimProcessed",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict",
            "Prod"."ProductCode", "Prod"."ProductName",
            "HFR"."RegionName" "Region", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        LEFT OUTER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems"
            WHERE "ValidityTo" IS NULL AND "ProdID" IS NOT NULL
            GROUP BY "ClaimID", "ProdID"
            UNION
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices"
            WHERE "ValidityTo" IS NULL AND "ProdID" IS NOT NULL
            GROUP BY "ClaimID", "ProdID"
        ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        LEFT OUTER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        LEFT OUTER JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
        WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" >= 8
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "HFD"."DistrictName", "Prod"."ProductCode", "Prod"."ProductName",
                "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwClaimRejected" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwClaimRejected" AS
        SELECT COUNT(1) "TotalClaimRejected",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
        WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" = 1
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwClaimSent" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwClaimSent" AS
        SELECT COUNT("C"."ClaimID") "ClaimSent",
            MONTH("C"."DateClaimed") MonthTime,
            QUARTER("C"."DateClaimed") QuarterTime,
            YEAR("C"."DateClaimed") YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFR"."RegionName" "Region", "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        INNER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems"
            WHERE "ValidityTo" IS NULL
            UNION
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices"
            WHERE "ValidityTo" IS NULL
        ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        INNER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "C"."ValidityTo" IS NULL
        AND "Prod"."ValidityTo" IS NULL
        AND "HF"."ValidityTo" IS NULL
        AND "HFD"."ValidityTo" IS NULL
        AND "C"."ClaimStatus" > 2
        GROUP BY MONTH("C"."DateClaimed"), QUARTER("C"."DateClaimed"),
                YEAR("C"."DateClaimed"), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "Prod"."ProductCode", "Prod"."ProductName", "HFD"."DistrictName",
                "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwClaimSubmitted" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwClaimSubmitted" AS
        SELECT COUNT(1) "TotalClaimSubmitted",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "C"."ValidityTo" IS NULL
        AND ("C"."ClaimStatus" >= 4 OR "C"."ClaimStatus" = 1)
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwClaimValuated" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwClaimValuated" AS
        SELECT COUNT(1) "TotalClaimValuated",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict",
            "Prod"."ProductCode", "Prod"."ProductName",
            "HFR"."RegionName" "Region", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        LEFT OUTER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems"
            WHERE "ValidityTo" IS NULL AND "ProdID" IS NOT NULL
            GROUP BY "ClaimID", "ProdID"
            UNION
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices"
            WHERE "ValidityTo" IS NULL AND "ProdID" IS NOT NULL
            GROUP BY "ClaimID", "ProdID"
        ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        LEFT OUTER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        LEFT OUTER JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
        WHERE "C"."ValidityTo" IS NULL
        AND "C"."ClaimStatus" = 16
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "HFD"."DistrictName", "Prod"."ProductCode", "Prod"."ProductName",
                "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwHospitalAdmissions" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwHospitalAdmissions" AS
        SELECT COUNT("C"."ClaimID") AS Admissions,
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS YearTime,
            "HFR"."RegionName" AS Region,
            "HFD"."DistrictName", "Prod"."ProductCode", "Prod"."ProductName",
            DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) AS "Age",
            "I"."Gender", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
            "HFD"."DistrictName" AS "HFDistrict", "HFR"."RegionName" AS "HFRegion"
        FROM public."tblClaim" AS "C"
        LEFT OUTER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM public."tblClaimItems"
            WHERE "ValidityTo" IS NULL AND "RejectionReason" = 0
            UNION
            SELECT "ClaimID", "ProdID"
            FROM public."tblClaimServices"
            WHERE "ValidityTo" IS NULL AND "RejectionReason" = 0
        ) AS "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        LEFT OUTER JOIN public."tblProduct" AS "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        LEFT OUTER JOIN public."tblInsuree" AS "I" ON "C"."InsureeID" = "I"."InsureeID"
        LEFT OUTER JOIN public."tblHF" AS "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN public."tblICDCodes" AS "ICD" ON "C"."ICDID" = "ICD"."ICDID"
        LEFT OUTER JOIN public."tblDistricts" AS "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        LEFT OUTER JOIN public."tblRegions" AS "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "C"."ValidityTo" IS NULL
        AND "Prod"."ValidityTo" IS NULL
        AND "I"."ValidityTo" IS NULL
        AND "HF"."ValidityTo" IS NULL
        AND "HFD"."ValidityTo" IS NULL
        AND DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0
        AND "C"."ClaimStatus" <> 1
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "Prod"."ProductCode", "Prod"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")),
                "I"."Gender", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwHospitalDays" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwHospitalDays" AS
        SELECT SUM(DATEDIFF_DAY("C"."DateFrom", "C"."DateTo")) AS HospitalDays,
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS YearTime,
            "HFR"."RegionName" AS Region, "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) AS "Age",
            "I"."Gender", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
            "HFD"."DistrictName" AS "HFDistrict", "HFR"."RegionName" AS "HFRegion"
        FROM public."tblClaim" AS "C"
        LEFT OUTER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM public."tblClaimItems"
            WHERE "ValidityTo" IS NULL AND "RejectionReason" = 0
            UNION
            SELECT "ClaimID", "ProdID"
            FROM public."tblClaimServices"
            WHERE "ValidityTo" IS NULL AND "RejectionReason" = 0
        ) AS "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        LEFT OUTER JOIN public."tblProduct" AS "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        LEFT OUTER JOIN public."tblInsuree" AS "I" ON "C"."InsureeID" = "I"."InsureeID"
        LEFT OUTER JOIN public."tblHF" AS "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN public."tblICDCodes" AS "ICD" ON "C"."ICDID" = "ICD"."ICDID"
        LEFT OUTER JOIN public."tblDistricts" AS "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        LEFT OUTER JOIN public."tblRegions" AS "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "C"."ValidityTo" IS NULL
        AND "Prod"."ValidityTo" IS NULL
        AND "I"."ValidityTo" IS NULL
        AND "HF"."ValidityTo" IS NULL
        AND "HFD"."ValidityTo" IS NULL
        AND DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0
        AND "C"."ClaimStatus" <> 1
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "Prod"."ProductCode", "Prod"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")),
                "I"."Gender", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwAmountApproved" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwAmountApproved" AS
        SELECT SUM("Details"."Approved") "AmountApproved",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFR"."RegionName" "Region", "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        LEFT OUTER JOIN (
            SELECT "ClaimID", "ProdID", SUM("PriceValuated") "Approved"
            FROM "tblClaimItems"
            WHERE "ValidityTo" IS NULL
            GROUP BY "ClaimID", "ProdID"
            UNION ALL
            SELECT "ClaimID", "ProdID", SUM("PriceValuated") "Approved"
            FROM "tblClaimServices"
            WHERE "ValidityTo" IS NULL
            GROUP BY "ClaimID", "ProdID"
        ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        LEFT OUTER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        LEFT OUTER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "C"."ValidityTo" IS NULL
        AND "C"."ClaimStatus" >= 8 -- Processed and greater
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "Prod"."ProductCode", "Prod"."ProductName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwNumberFeedbackAnswerYes" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwNumberFeedbackAnswerYes" AS
        SELECT COUNT("F"."FeedbackID") "AnsYes", 1 "QuestionId",
            MONTH("F"."FeedbackDate") MonthTime,
            QUARTER("F"."FeedbackDate") QuarterTime,
            YEAR("F"."FeedbackDate") YearTime,
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFR"."RegionName" "Region", "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName"
        FROM "tblFeedback" "F"
        INNER JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
        INNER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems" WHERE "ValidityTo" IS NULL
            UNION 
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices" WHERE "ValidityTo" IS NULL
        ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        INNER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "F"."ValidityTo" IS NULL AND "F"."CareRendered" = TRUE
        GROUP BY MONTH("F"."FeedbackDate"), QUARTER("F"."FeedbackDate"),
                YEAR("F"."FeedbackDate"), "HF"."HFLevel", "HF"."HFCode",
                "HF"."HFName", "Prod"."ProductCode", "Prod"."ProductName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwNumberFeedbackResponded" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwNumberFeedbackResponded" AS
        SELECT COUNT("F"."FeedbackID") "FeedbackResponded",
            MONTH("F"."FeedbackDate") MonthTime,
            QUARTER("F"."FeedbackDate") QuarterTime,
            YEAR("F"."FeedbackDate") YearTime,
            "HFR"."RegionName" "Region", "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblFeedback" "F"
        INNER JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
        INNER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems" WHERE "ValidityTo" IS NULL
            UNION 
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices" WHERE "ValidityTo" IS NULL
        ) "Details" ON "F"."ClaimID" = "Details"."ClaimID"
        INNER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "F"."ValidityTo" IS NULL
        GROUP BY YEAR("F"."FeedbackDate"), MONTH("F"."FeedbackDate"),
                QUARTER("F"."FeedbackDate"), "Prod"."ProductCode",
                "Prod"."ProductName", "HF"."HFLevel", "HF"."HFCode",
                "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwNumberFeedbackSent" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwNumberFeedbackSent" AS
        SELECT COUNT("FeedbackPromptID") "FeedbackSent",
            MONTH("F"."FeedbackPromptDate") MonthTime,
            QUARTER("F"."FeedbackPromptDate") QuarterTime,
            YEAR("F"."FeedbackPromptDate") YearTime,
            "HFR"."RegionName" "Region", "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblFeedbackPrompt" "F"
        INNER JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
        INNER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems" WHERE "ValidityTo" IS NULL
            UNION 
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices" WHERE "ValidityTo" IS NULL
        ) "Details" ON "F"."ClaimID" = "Details"."ClaimID"
        INNER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "F"."ValidityTo" IS NULL
        GROUP BY YEAR("F"."FeedbackPromptDate"), MONTH("F"."FeedbackPromptDate"),
                QUARTER("F"."FeedbackPromptDate"), "Prod"."ProductCode",
                "Prod"."ProductName", "HF"."HFLevel", "HF"."HFCode",
                "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwOverallAssessment" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwOverallAssessment" AS
        SELECT "Asessment",
            MONTH("FeedbackDate") MonthTime,
            QUARTER("FeedbackDate") QuarterTime,
            YEAR("FeedbackDate") YearTime,
            "HFR"."RegionName" "Region", "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblFeedback" "F"
        INNER JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
        INNER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems" WHERE "ValidityTo" IS NULL
            UNION 
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices" WHERE "ValidityTo" IS NULL
        ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        INNER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "F"."ValidityTo" IS NULL
        AND "C"."ValidityTo" IS NULL
        AND "Prod"."ValidityTo" IS NULL
        AND "HF"."ValidityTo" IS NULL
        AND "HFD"."ValidityTo" IS NULL;
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwVisit" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwVisit" AS
        SELECT COUNT("C"."ClaimID") "Visits",
            MONTH("C"."DateFrom") MonthTime,
            QUARTER("C"."DateFrom") QuarterTime,
            YEAR("C"."DateFrom") YearTime,
            "HFR"."RegionName" "Region", "HFD"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            DATEDIFF_YEAR("I"."DOB", "C"."DateFrom") "Age", "I"."Gender",
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion"
        FROM "tblClaim" "C"
        LEFT OUTER JOIN (
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimItems" WHERE "ValidityTo" IS NULL AND "RejectionReason" = 0
            UNION 
            SELECT "ClaimID", "ProdID"
            FROM "tblClaimServices" WHERE "ValidityTo" IS NULL AND "RejectionReason" = 0
        ) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
        LEFT OUTER JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
        LEFT OUTER JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
        LEFT OUTER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        LEFT OUTER JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
        LEFT OUTER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        LEFT OUTER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "C"."ValidityTo" IS NULL
        AND "Prod"."ValidityTo" IS NULL
        AND "I"."ValidityTo" IS NULL
        AND "HF"."ValidityTo" IS NULL
        AND "HFD"."ValidityTo" IS NULL
        AND DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") = 0
        GROUP BY MONTH("C"."DateFrom"), QUARTER("C"."DateFrom"), YEAR("C"."DateFrom"),
                "Prod"."ProductCode", "Prod"."ProductName",
                DATEDIFF_YEAR("I"."DOB", "C"."DateFrom"), "I"."Gender",
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwItemUtilization" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwItemUtilization" AS
        SELECT SUM("CI"."QtyProvided") AS "ItemUtilized",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS YearTime,
            "R"."RegionName" AS "Region", "DIns"."DistrictName",
            "Prod"."ProductCode", "Prod"."ProductName",
            DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) AS "Age",
            "I"."Gender", "Itm"."ItemType", "Itm"."ItemCode", "Itm"."ItemName",
            CASE WHEN DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0 THEN N'I' ELSE N'O' END AS "ItemCareType",
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "ICD"."ICDCode", "ICD"."ICDName"
        FROM public."tblClaimItems" AS "CI"
        INNER JOIN public."tblClaim" AS "C" ON "C"."ClaimID" = "CI"."ClaimID"
        LEFT OUTER JOIN public."tblProduct" AS "Prod" ON "CI"."ProdID" = "Prod"."ProdID"
        INNER JOIN public."tblInsuree" AS "I" ON "C"."InsureeID" = "I"."InsureeID"
        INNER JOIN public."tblItems" AS "Itm" ON "CI"."ItemID" = "Itm"."ItemID"
        INNER JOIN public."tblHF" AS "HF" ON "C"."HFID" = "HF"."HfID"
        INNER JOIN public."tblICDCodes" AS "ICD" ON "C"."ICDID" = "ICD"."ICDID"
        INNER JOIN public."tblDistricts" AS "DIns" ON "HF"."LocationId" = "DIns"."DistrictId"
        INNER JOIN public."tblRegions" AS "R" ON "DIns"."Region" = "R"."RegionId"
        WHERE "CI"."ValidityTo" IS NULL
        AND "C"."ValidityTo" IS NULL
        AND "Prod"."ValidityTo" IS NULL
        AND "Itm"."ValidityTo" IS NULL
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "R"."RegionName", "DIns"."DistrictName",
                "Prod"."ProductCode", "Prod"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")),
                "I"."Gender", "Itm"."ItemType", "Itm"."ItemCode", "Itm"."ItemName",
                DATEDIFF_DAY("C"."DateFrom", "C"."DateTo"),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "ICD"."ICDCode", "ICD"."ICDName";
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwServiceUtilization" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwServiceUtilization" AS
        SELECT SUM("CS"."QtyProvided") AS "ServiceUtilized",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) AS MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) AS QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) AS YearTime,
            "R"."RegionName" AS "Region", "DIns"."DistrictName",
            "S"."ServType", "S"."ServCode", "S"."ServName",
            CASE WHEN DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0 THEN N'I' ELSE N'O' END AS "ServiceCareType"
        FROM public."tblClaimServices" AS "CS"
        INNER JOIN public."tblClaim" AS "C" ON "CS"."ClaimID" = "C"."ClaimID"
        INNER JOIN public."tblServices" AS "S" ON "CS"."ServiceID" = "S"."ServiceID"
        INNER JOIN public."tblDistricts" AS "DIns" ON "C"."HFID" = "DIns"."DistrictId"
        INNER JOIN public."tblRegions" AS "R" ON "DIns"."Region" = "R"."RegionId"
        WHERE "CS"."ValidityTo" IS NULL
        AND "C"."ValidityTo" IS NULL
        AND "S"."ValidityTo" IS NULL
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "R"."RegionName", "DIns"."DistrictName",
                "S"."ServType", "S"."ServCode", "S"."ServName",
                DATEDIFF_DAY("C"."DateFrom", "C"."DateTo");
            """
        ),
        migrations.RunSQL(
            """
            -- Recrée la vue "uvwItemExpenditures" pour les montants rejetés
            CREATE OR REPLACE VIEW "public"."uvwItemExpenditures" AS
        SELECT SUM("CI"."RemuneratedAmount") "ItemExpenditure",
            MONTH(coalesce("C"."DateTo", "C"."DateFrom")) MonthTime,
            QUARTER(coalesce("C"."DateTo", "C"."DateFrom")) QuarterTime,
            YEAR(coalesce("C"."DateTo", "C"."DateFrom")) YearTime,
            "R"."RegionName" "Region", "HFD"."DistrictName",
            "PR"."ProductCode", "PR"."ProductName",
            DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")) "Age",
            "I"."Gender", "Itm"."ItemType", "Itm"."ItemCode", "Itm"."ItemName",
            CASE WHEN DATEDIFF_DAY("C"."DateFrom", "C"."DateTo") > 0 THEN N'I' ELSE N'O' END "ItemCareType",
            "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
            "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
            "DIns"."DistrictName" "IDistrictName", "W"."WardName", "V"."VillageName",
            "HFD"."DistrictName" "HFDistrict", "HFR"."RegionName" "HFRegion",
            "HFR"."RegionName" "ProdRegion"
        FROM "tblClaimItems" "CI"
        INNER JOIN "tblClaim" "C" ON "CI"."ClaimID" = "C"."ClaimID"
        INNER JOIN "tblProduct" "PR" ON "CI"."ProdID" = "PR"."ProdID"
        INNER JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
        INNER JOIN "tblFamilies" "F" ON "I"."FamilyID" = "F"."FamilyID"
        INNER JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
        INNER JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
        INNER JOIN "tblDistricts" "DIns" ON "DIns"."DistrictId" = "W"."DistrictId"
        INNER JOIN "tblItems" "Itm" ON "CI"."ItemID" = "Itm"."ItemID"
        INNER JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
        INNER JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
        INNER JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
        INNER JOIN "tblRegions" "R" ON "DIns"."Region" = "R"."RegionId"
        INNER JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
        WHERE "CI"."ValidityTo" IS NULL
        AND "C"."ValidityTo" IS NULL
        AND "PR"."ValidityTo" IS NULL
        AND "I"."ValidityTo" IS NULL
        AND "HF"."ValidityTo" IS NULL
        AND "HFD"."ValidityTo" IS NULL
        AND "C"."ClaimStatus" >= 8 -- Processed or Valuated Claims
        GROUP BY MONTH(coalesce("C"."DateTo", "C"."DateFrom")),
                QUARTER(coalesce("C"."DateTo", "C"."DateFrom")),
                YEAR(coalesce("C"."DateTo", "C"."DateFrom")),
                "R"."RegionName", "PR"."ProductCode", "PR"."ProductName",
                DATEDIFF_YEAR("I"."DOB", coalesce("C"."DateTo", "C"."DateFrom")),
                "I"."Gender", "Itm"."ItemType", "Itm"."ItemCode", "Itm"."ItemName",
                DATEDIFF_DAY("C"."DateFrom", "C"."DateTo"),
                "HF"."HFLevel", "HF"."HFCode", "HF"."HFName",
                "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName",
                "DIns"."DistrictName", "W"."WardName", "V"."VillageName",
                "HFD"."DistrictName", "HFR"."RegionName";
            """
        ),

    ]