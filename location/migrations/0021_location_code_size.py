from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0018_auto_20230925_2243'),
    ]

    operations = [

        migrations.RunSQL(
            """
            -- Delete View first
            DROP VIEW IF EXISTS public."uvwExpenditureInsureeRange";
            DROP VIEW IF EXISTS public."uvwLocations";
            DROP VIEW IF EXISTS public."uvwNumberInsureeAcquired";
            DROP VIEW IF EXISTS public."uvwNumberOfInsuredHouseholds";
            DROP VIEW IF EXISTS public."uvwNumberPolicyRenewed";
            DROP VIEW IF EXISTS public."uvwNumberPolicySold";
            DROP VIEW IF EXISTS public."uvwPopulation";
            DROP VIEW IF EXISTS public."uvwPremiumCollection";
            DROP VIEW IF EXISTS public."uvwpremiumcollection";
            DROP VIEW IF EXISTS public."uvwAmountRejected";
            DROP VIEW IF EXISTS public."uvwAmountClaimed";
            DROP VIEW IF EXISTS public."uvwAmountValuated";
            DROP VIEW IF EXISTS public."uvwClaimEntered";
            DROP VIEW IF EXISTS public."uvwClaimProcessed";
            DROP VIEW IF EXISTS public."uvwClaimRejected";
            DROP VIEW IF EXISTS public."uvwClaimSent";
            DROP VIEW IF EXISTS public."uvwClaimSubmitted";
            DROP VIEW IF EXISTS public."uvwClaimValuated";
            DROP VIEW IF EXISTS public."uvwHospitalAdmissions";
            DROP VIEW IF EXISTS public."uvwHospitalDays";
            DROP VIEW IF EXISTS public."uvwAmountApproved";
            DROP VIEW IF EXISTS public."uvwNumberFeedbackAnswerYes";
            DROP VIEW IF EXISTS public."uvwNumberFeedbackResponded";
            DROP VIEW IF EXISTS public."uvwNumberFeedbackSent";
            DROP VIEW IF EXISTS public."uvwOverallAssessment";
            DROP VIEW IF EXISTS public."uvwVisit";
            DROP VIEW IF EXISTS public."uvwItemUtilization";
            DROP VIEW IF EXISTS public."uvwServiceUtilization";
            DROP VIEW IF EXISTS public."uvwItemExpenditures";
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


            CREATE OR REPLACE VIEW public."uvwExpenditureInsureeRange"
            AS
            WITH "Val" AS (
                    SELECT "tblClaimItems"."ClaimID",
                        sum("tblClaimItems"."PriceValuated") AS "Valuated",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL AND "tblClaimItems"."PriceValuated" IS NOT NULL
                    GROUP BY "tblClaimItems"."ClaimID", "tblClaimItems"."ProdID"
                    UNION ALL
                    SELECT "tblClaimServices"."ClaimID",
                        sum("tblClaimServices"."PriceValuated") AS "Valuated",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL AND "tblClaimServices"."PriceValuated" IS NOT NULL
                    GROUP BY "tblClaimServices"."ClaimID", "tblClaimServices"."ProdID"
                    )
            SELECT sum("Val"."Valuated") AS "Valuated",
                "C"."ClaimID" AS "Insuree",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "R"."RegionName" AS "Region",
                "D"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom")) AS "Age",
                "I"."Gender"
            FROM "Val"
                JOIN "tblClaim" "C" ON "Val"."ClaimID" = "C"."ClaimID"
                JOIN "tblProduct" "Prod" ON "Val"."ProdID" = "Prod"."ProdID"
                JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
                JOIN "tblFamilies" "F" ON "F"."InsureeID" = "I"."InsureeID"
                JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
                JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
                JOIN "tblDistricts" "D" ON "D"."DistrictId" = "W"."DistrictId"
                JOIN "tblRegions" "R" ON "R"."RegionId" = "D"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "F"."ValidityTo" IS NULL AND "D"."ValidityTo" IS NULL
            GROUP BY "C"."ClaimID", (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "R"."RegionName", "D"."DistrictName", "Prod"."ProductCode", "Prod"."ProductName", (datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom"))), "I"."Gender";


            CREATE OR REPLACE VIEW public."uvwLocations"
            AS
            SELECT 0 AS "LocationId",
                NULL::integer AS "RegionId",
                NULL::character varying AS "RegionCode",
                'National'::bpchar AS "RegionName",
                NULL::text AS "DistrictId",
                NULL::text AS "DistrictCode",
                NULL::text AS "DistrictName",
                NULL::text AS "WardId",
                NULL::text AS "WardCode",
                NULL::text AS "WardName",
                NULL::text AS "VillageId",
                NULL::text AS "VillageCode",
                NULL::text AS "VillageName",
                NULL::integer AS "ParentLocationId"
            UNION ALL
            SELECT "tblRegions"."RegionId" AS "LocationId",
                "tblRegions"."RegionId",
                "tblRegions"."RegionCode",
                "tblRegions"."RegionName",
                NULL::text AS "DistrictId",
                NULL::text AS "DistrictCode",
                NULL::text AS "DistrictName",
                NULL::text AS "WardId",
                NULL::text AS "WardCode",
                NULL::text AS "WardName",
                NULL::text AS "VillageId",
                NULL::text AS "VillageCode",
                NULL::text AS "VillageName",
                0 AS "ParentLocationId"
            FROM "tblRegions"
            UNION ALL
            SELECT "D"."DistrictId" AS "LocationId",
                "R"."RegionId",
                "R"."RegionCode",
                "R"."RegionName",
                "D"."DistrictId"::text AS "DistrictId",
                "D"."DistrictCode",
                "D"."DistrictName",
                NULL::text AS "WardId",
                NULL::text AS "WardCode",
                NULL::text AS "WardName",
                NULL::text AS "VillageId",
                NULL::text AS "VillageCode",
                NULL::text AS "VillageName",
                "D"."Region" AS "ParentLocationId"
            FROM "tblDistricts" "D"
                JOIN "tblRegions" "R" ON "R"."RegionId" = "D"."Region"
            UNION ALL
            SELECT "W"."WardId" AS "LocationId",
                "R"."RegionId",
                "R"."RegionCode",
                "R"."RegionName",
                "D"."DistrictId"::text AS "DistrictId",
                "D"."DistrictCode",
                "D"."DistrictName",
                "W"."WardId"::text AS "WardId",
                "W"."WardCode",
                "W"."WardName",
                NULL::text AS "VillageId",
                NULL::text AS "VillageCode",
                NULL::text AS "VillageName",
                "D"."DistrictId" AS "ParentLocationId"
            FROM "tblRegions" "R"
                JOIN "tblDistricts" "D" ON "R"."RegionId" = "D"."Region"
                JOIN "tblWards" "W" ON "W"."DistrictId" = "D"."DistrictId"
            UNION ALL
            SELECT "V"."VillageId" AS "LocationId",
                "R"."RegionId",
                "R"."RegionCode",
                "R"."RegionName",
                "D"."DistrictId"::text AS "DistrictId",
                "D"."DistrictCode",
                "D"."DistrictName",
                "W"."WardId"::text AS "WardId",
                "W"."WardCode",
                "W"."WardName",
                "V"."VillageId"::text AS "VillageId",
                "V"."VillageCode",
                "V"."VillageName",
                "V"."WardId" AS "ParentLocationId"
            FROM "tblRegions" "R"
                JOIN "tblDistricts" "D" ON "R"."RegionId" = "D"."Region"
                JOIN "tblWards" "W" ON "W"."DistrictId" = "D"."DistrictId"
                JOIN "tblVillages" "V" ON "V"."WardId" = "W"."WardId";

                
            CREATE OR REPLACE VIEW public."uvwNumberInsureeAcquired"
            AS
            SELECT count("I"."InsureeID") AS "NewInsurees",
                month("PL"."EnrollDate") AS monthtime,
                datename_q("PL"."EnrollDate") AS quartertime,
                year("PL"."EnrollDate") AS yeartime,
                datediff_year("I"."DOB"::timestamp with time zone, now()) AS "Age",
                "I"."Gender",
                "R"."RegionName" AS "Region",
                "D"."DistrictName" AS "InsDistrict",
                "V"."VillageName" AS "InsVillage",
                "W"."WardName" AS "InsWard",
                "D"."DistrictName" AS "ProdDistrict",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "ODist"."DistrictName" AS "OfficerDistrict",
                "O"."Code",
                "O"."LastName",
                "O"."OtherNames",
                "R"."RegionName" AS "ProdRegion"
            FROM "tblPolicy" "PL"
                JOIN "tblInsuree" "I" ON "PL"."FamilyID" = "I"."FamilyID"
                JOIN "tblProduct" "Prod" ON "PL"."ProdID" = "Prod"."ProdID"
                JOIN "tblFamilies" "F" ON "PL"."FamilyID" = "F"."FamilyID"
                JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
                JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
                JOIN "tblDistricts" "D" ON "D"."DistrictId" = "W"."DistrictId"
                JOIN "tblOfficer" "O" ON "PL"."OfficerID" = "O"."OfficerID"
                JOIN "tblDistricts" "ODist" ON "O"."LocationId" = "ODist"."DistrictId"
                JOIN "tblInsureePolicy" "InsPL" ON "InsPL"."InsureeID" = "I"."InsureeID" AND "InsPL"."PolicyId" = "PL"."PolicyID"
                JOIN "tblRegions" "R" ON "R"."RegionId" = "D"."Region"
            WHERE "PL"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "F"."ValidityTo" IS NULL AND "D"."ValidityTo" IS NULL AND "V"."ValidityTo" IS NULL AND "W"."ValidityTo" IS NULL AND "O"."ValidityTo" IS NULL AND "ODist"."ValidityTo" IS NULL AND "InsPL"."ValidityTo" IS NULL
            GROUP BY (month("PL"."EnrollDate")), (datename_q("PL"."EnrollDate")), (year("PL"."EnrollDate")), (datediff_year("I"."DOB"::timestamp with time zone, now())), "I"."Gender", "D"."DistrictName", "V"."VillageName", "W"."WardName", "R"."RegionName", "Prod"."ProductCode", "Prod"."ProductName", "ODist"."DistrictName", "O"."Code", "O"."LastName", "O"."OtherNames";


            CREATE OR REPLACE VIEW public."uvwNumberOfInsuredHouseholds"
            AS
            WITH "RowData" AS (
                    SELECT "F"."FamilyID",
                        eomonth("PL"."EffectiveDate") + "MonthCount".numbers::double precision * '1 mon'::interval AS "ActiveDate",
                        "R"."RegionName" AS "Region",
                        "D"."DistrictName",
                        "W"."WardName",
                        "V"."VillageName"
                    FROM "tblPolicy" "PL"
                        JOIN "tblFamilies" "F" ON "PL"."FamilyID" = "F"."FamilyID"
                        JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
                        JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
                        JOIN "tblDistricts" "D" ON "D"."DistrictId" = "W"."DistrictId"
                        JOIN "tblRegions" "R" ON "D"."Region" = "R"."RegionId"
                        LEFT JOIN LATERAL ( VALUES (0), (1), (2), (3), (4), (5), (6), (7), (8), (9), (10), (11)) "MonthCount"(numbers) ON true
                    WHERE "PL"."ValidityTo" IS NULL AND "F"."ValidityTo" IS NULL AND "R"."ValidityTo" IS NULL AND "D"."ValidityTo" IS NULL AND "W"."ValidityTo" IS NULL AND "V"."ValidityTo" IS NULL AND "PL"."EffectiveDate" IS NOT NULL
                    ), "RowData2" AS (
                    SELECT "RowData"."FamilyID",
                        "RowData"."ActiveDate",
                        "RowData"."Region",
                        "RowData"."DistrictName",
                        "RowData"."WardName",
                        "RowData"."VillageName"
                    FROM "RowData"
                    GROUP BY "RowData"."FamilyID", "RowData"."ActiveDate", "RowData"."Region", "RowData"."DistrictName", "RowData"."WardName", "RowData"."VillageName"
                    )
            SELECT count("RowData2"."FamilyID") AS "InsuredHouseholds",
                month("RowData2"."ActiveDate") AS monthtime,
                datename_q("RowData2"."ActiveDate") AS quartertime,
                year("RowData2"."ActiveDate") AS yeartime,
                "RowData2"."Region",
                "RowData2"."DistrictName",
                "RowData2"."WardName",
                "RowData2"."VillageName"
            FROM "RowData2"
            GROUP BY "RowData2"."ActiveDate", "RowData2"."Region", "RowData2"."DistrictName", "RowData2"."WardName", "RowData2"."VillageName";

            CREATE OR REPLACE VIEW public."uvwNumberPolicyRenewed"
            AS
            SELECT count("PL"."FamilyID") AS "Renewals",
                month("PL"."EnrollDate") AS monthtime,
                datename_q("PL"."EnrollDate") AS quartertime,
                year("PL"."EnrollDate") AS yeartime,
                datediff_year("I"."DOB", "PL"."EnrollDate") AS "Age",
                "I"."Gender",
                "R"."RegionName" AS "Region",
                "FD"."DistrictName" AS "InsureeDistrictName",
                "FV"."VillageName",
                "FW"."WardName",
                "FD"."DistrictName" AS "Prod""DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "OD"."DistrictName" AS "OfficeDistrict",
                "O"."Code" AS "OfficerCode",
                "O"."LastName",
                "O"."OtherNames",
                "R"."RegionName" AS "ProdRegion"
            FROM "tblPolicy" "PL"
                JOIN "tblFamilies" "F" ON "PL"."FamilyID" = "F"."FamilyID"
                JOIN "tblInsuree" "I" ON "F"."InsureeID" = "I"."InsureeID"
                JOIN "tblVillages" "FV" ON "FV"."VillageId" = "F"."LocationId"
                JOIN "tblWards" "FW" ON "FW"."WardId" = "FV"."WardId"
                JOIN "tblDistricts" "FD" ON "FD"."DistrictId" = "FW"."DistrictId"
                JOIN "tblProduct" "Prod" ON "PL"."ProdID" = "Prod"."ProdID"
                JOIN "tblOfficer" "O" ON "PL"."OfficerID" = "O"."OfficerID"
                JOIN "tblDistricts" "OD" ON "OD"."DistrictId" = "O"."LocationId"
                JOIN "tblRegions" "R" ON "R"."RegionId" = "FD"."Region"
            WHERE "PL"."ValidityTo" IS NULL AND "F"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "FD"."ValidityTo" IS NULL AND "FW"."ValidityTo" IS NULL AND "FV"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "O"."ValidityTo" IS NULL AND "OD"."ValidityTo" IS NULL AND "PL"."PolicyStage"::bpchar = 'R'::bpchar
            GROUP BY (month("PL"."EnrollDate")), (datename_q("PL"."EnrollDate")), (year("PL"."EnrollDate")), (datediff_year("I"."DOB", "PL"."EnrollDate")), "I"."Gender", "R"."RegionName", "FD"."DistrictName", "FV"."VillageName", "FW"."WardName", "Prod"."ProductCode", "Prod"."ProductName", "OD"."DistrictName", "O"."Code", "O"."LastName", "O"."OtherNames";

            CREATE OR REPLACE VIEW public."uvwNumberPolicySold"
            AS
            SELECT count("PL"."FamilyID") AS soldpolicy,
                month("PL"."EnrollDate") AS monthtime,
                datename_q("PL"."EnrollDate") AS quartertime,
                year("PL"."EnrollDate") AS yeartime,
                datediff_year("I"."DOB", "PL"."EnrollDate") AS "Age",
                "I"."Gender",
                "RD"."RegionName" AS "Region",
                "FD"."DistrictName" AS "InsDistrict",
                "FV"."VillageName" AS "InsVillage",
                "FW"."WardName" AS "InsWard",
                "FD"."DistrictName" AS "ProdDistrict",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "OD"."DistrictName" AS "OfficerDistrict",
                "O"."Code",
                "O"."LastName",
                "O"."OtherNames",
                "RD"."RegionName" AS "ProdRegion"
            FROM "tblPolicy" "PL"
                JOIN "tblFamilies" "F" ON "PL"."FamilyID" = "F"."FamilyID"
                JOIN "tblInsuree" "I" ON "F"."InsureeID" = "I"."InsureeID"
                JOIN "tblVillages" "FV" ON "FV"."VillageId" = "F"."LocationId"
                JOIN "tblWards" "FW" ON "FW"."WardId" = "FV"."WardId"
                JOIN "tblDistricts" "FD" ON "FD"."DistrictId" = "FW"."DistrictId"
                JOIN "tblProduct" "Prod" ON "PL"."ProdID" = "Prod"."ProdID"
                JOIN "tblOfficer" "O" ON "PL"."OfficerID" = "O"."OfficerID"
                JOIN "tblDistricts" "OD" ON "OD"."DistrictId" = "O"."LocationId"
                JOIN "tblRegions" "RD" ON "RD"."RegionId" = "FD"."Region"
            WHERE "PL"."ValidityTo" IS NULL AND "F"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "FD"."ValidityTo" IS NULL AND "FW"."ValidityTo" IS NULL AND "FV"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "O"."ValidityTo" IS NULL AND "OD"."ValidityTo" IS NULL AND "PL"."PolicyStage"::bpchar = 'N'::bpchar
            GROUP BY (month("PL"."EnrollDate")), (datename_q("PL"."EnrollDate")), (year("PL"."EnrollDate")), (datediff_year("I"."DOB", "PL"."EnrollDate")), "I"."Gender", "RD"."RegionName", "FD"."DistrictName", "FV"."VillageName", "FW"."WardName", "Prod"."ProductCode", "Prod"."ProductName", "OD"."DistrictName", "O"."Code", "O"."LastName", "O"."OtherNames";

            
            CREATE OR REPLACE VIEW public."uvwPopulation"
            AS
            SELECT "R"."RegionName" AS "Region",
                "D"."DistrictName" AS "District",
                "W"."WardName" AS "Ward",
                "V"."VillageName" AS "Village",
                "V"."MalePopulation" AS "Male",
                "V"."FemalePopulation" AS "Female",
                "V"."OtherPopulation" AS others,
                "V"."Families" AS "Households",
                date_part('year'::text, now()) AS "YEAR"
            FROM "tblVillages" "V"
                JOIN "tblWards" "W" ON "V"."WardId" = "W"."WardId"
                JOIN "tblDistricts" "D" ON "D"."DistrictId" = "W"."DistrictId"
                JOIN "tblRegions" "R" ON "R"."RegionId" = "D"."Region"
            WHERE "V"."ValidityTo" IS NULL AND "W"."ValidityTo" IS NULL AND "D"."ValidityTo" IS NULL AND "R"."ValidityTo" IS NULL;


            CREATE OR REPLACE VIEW public."uvwPremiumCollection"
            AS
            SELECT sum("PR"."Amount") AS "Amount",
                "PR"."PayType",
                "Pay"."PayerType",
                "Pay"."PayerName",
                "R"."RegionName" AS "Region",
                "FD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "O"."Code",
                "O"."LastName",
                "O"."OtherNames",
                "DO"."DistrictName" AS "OfficerDistrict",
                month("PR"."PayDate") AS monthtime,
                datename_q("PR"."PayDate") AS quartertime,
                year("PR"."PayDate") AS yeartime
            FROM "tblPremium" "PR"
                LEFT JOIN "tblPayer" "Pay" ON "PR"."PayerID" = "Pay"."PayerID"
                JOIN "tblPolicy" "PL" ON "PR"."PolicyID" = "PL"."PolicyID"
                JOIN "tblProduct" "Prod" ON "PL"."ProdID" = "Prod"."ProdID"
                JOIN "tblOfficer" "O" ON "PL"."OfficerID" = "O"."OfficerID"
                JOIN "tblDistricts" "DO" ON "O"."LocationId" = "DO"."DistrictId"
                JOIN "tblFamilies" "F" ON "PL"."FamilyID" = "F"."FamilyID"
                JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
                JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
                JOIN "tblDistricts" "FD" ON "FD"."DistrictId" = "W"."DistrictId"
                JOIN "tblRegions" "R" ON "R"."RegionId" = "FD"."Region"
            WHERE "PR"."ValidityTo" IS NULL AND "Pay"."ValidityTo" IS NULL AND "PL"."ValidityTo" IS NULL AND "F"."ValidityTo" IS NULL
            GROUP BY "PR"."PayType", "Pay"."PayerType", "Pay"."PayerName", "R"."RegionName", "Prod"."ProductCode", "Prod"."ProductName", "O"."Code", "O"."LastName", "O"."OtherNames", "DO"."DistrictName", (month("PR"."PayDate")), (datename_q("PR"."PayDate")), (year("PR"."PayDate")), "FD"."DistrictName";

            CREATE OR REPLACE VIEW public."uvwAmountRejected"
            AS
            SELECT sum("Details"."Rejected") AS amountrejected,
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS "MonthTime",
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS "QuarterTime",
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS "YearTime",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID",
                        sum("tblClaimItems"."QtyProvided" * "tblClaimItems"."PriceAsked") AS "Rejected"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    GROUP BY "tblClaimItems"."ClaimID", "tblClaimItems"."ProdID"
                    UNION ALL
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID",
                        sum("tblClaimServices"."QtyProvided" * "tblClaimServices"."PriceAsked") AS "Rejected"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL
                    GROUP BY "tblClaimServices"."ClaimID", "tblClaimServices"."ProdID") "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "HF"."ValidityTo" IS NULL AND "HFD"."ValidityTo" IS NULL AND "C"."ClaimStatus" = 1
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "Prod"."ProductCode", "Prod"."ProductName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwClaimRejected"
            AS
            SELECT count(1) AS "TotalClaimRejected",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
            WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" = 1
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";

            
            
            CREATE OR REPLACE VIEW public."uvwAmountClaimed"
            AS
            SELECT sum("Details"."Claimed") AS "AmountClaimed",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID",
                        sum("tblClaimItems"."QtyProvided" * "tblClaimItems"."PriceAsked") AS "Claimed"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    GROUP BY "tblClaimItems"."ClaimID", "tblClaimItems"."ProdID"
                    UNION ALL
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID",
                        sum("tblClaimServices"."QtyProvided" * "tblClaimServices"."PriceAsked") AS "Claimed"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL
                    GROUP BY "tblClaimServices"."ClaimID", "tblClaimServices"."ProdID") "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" <> 2
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "Prod"."ProductCode", "Prod"."ProductName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwAmountValuated"
            AS
            SELECT sum("Details"."Valuated") AS "AmountValuated",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID",
                        sum("tblClaimItems"."RemuneratedAmount") AS "Valuated"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    GROUP BY "tblClaimItems"."ClaimID", "tblClaimItems"."ProdID"
                    UNION ALL
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID",
                        sum("tblClaimServices"."RemuneratedAmount") AS "Valuated"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL
                    GROUP BY "tblClaimServices"."ClaimID", "tblClaimServices"."ProdID") "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" = 16
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "Prod"."ProductCode", "Prod"."ProductName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwClaimEntered"
            AS
            SELECT count(1) AS "TotalClaimEntered",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
            WHERE "C"."ValidityTo" IS NULL
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwClaimProcessed"
            AS
            SELECT count(1) AS "TotalClaimProcessed",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HFR"."RegionName" AS "Region",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL AND "tblClaimItems"."ProdID" IS NOT NULL
                    GROUP BY "tblClaimItems"."ClaimID", "tblClaimItems"."ProdID"
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL AND "tblClaimServices"."ProdID" IS NOT NULL
                    GROUP BY "tblClaimServices"."ClaimID", "tblClaimServices"."ProdID") "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
            WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" >= 8
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "Prod"."ProductCode", "Prod"."ProductName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwClaimRejected"
            AS
            SELECT count(1) AS "TotalClaimRejected",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
            WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" = 1
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";

            
            CREATE OR REPLACE VIEW public."uvwClaimSent"
            AS
            SELECT count("C"."ClaimID") AS "ClaimSent",
                month("C"."DateClaimed") AS monthtime,
                quarter("C"."DateClaimed") AS quartertime,
                year("C"."DateClaimed") AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "HF"."ValidityTo" IS NULL AND "HFD"."ValidityTo" IS NULL AND "C"."ClaimStatus" > 2
            GROUP BY (month("C"."DateClaimed")), (quarter("C"."DateClaimed")), (year("C"."DateClaimed")), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "Prod"."ProductCode", "Prod"."ProductName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwClaimSubmitted"
            AS
            SELECT count(1) AS "TotalClaimSubmitted",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND ("C"."ClaimStatus" >= 4 OR "C"."ClaimStatus" = 1)
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";

                                    
                        CREATE OR REPLACE VIEW public."uvwClaimValuated"
                        AS
                        SELECT count(1) AS "TotalClaimValuated",
                            month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                            quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                            year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                            "HF"."HFLevel",
                            "HF"."HFCode",
                            "HF"."HFName",
                            "HFD"."DistrictName" AS "HFDistrict",
                            "Prod"."ProductCode",
                            "Prod"."ProductName",
                            "HFR"."RegionName" AS "Region",
                            "HFR"."RegionName" AS "HFRegion"
                        FROM "tblClaim" "C"
                            LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                                    "tblClaimItems"."ProdID"
                                FROM "tblClaimItems"
                                WHERE "tblClaimItems"."ValidityTo" IS NULL AND "tblClaimItems"."ProdID" IS NOT NULL
                                GROUP BY "tblClaimItems"."ClaimID", "tblClaimItems"."ProdID"
                                UNION
                                SELECT "tblClaimServices"."ClaimID",
                                    "tblClaimServices"."ProdID"
                                FROM "tblClaimServices"
                                WHERE "tblClaimServices"."ValidityTo" IS NULL AND "tblClaimServices"."ProdID" IS NOT NULL
                                GROUP BY "tblClaimServices"."ClaimID", "tblClaimServices"."ProdID") "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                            LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                            LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                            LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                            LEFT JOIN "tblRegions" "HFR" ON "HFD"."Region" = "HFR"."RegionId"
                        WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" = 16
                        GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "Prod"."ProductCode", "Prod"."ProductName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwHospitalAdmissions"
            AS
            SELECT count("C"."ClaimID") AS admissions,
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HFR"."RegionName" AS region,
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom")) AS "Age",
                "I"."Gender",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL AND "tblClaimItems"."RejectionReason" = 0
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL AND "tblClaimServices"."RejectionReason" = 0) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "HF"."ValidityTo" IS NULL AND "HFD"."ValidityTo" IS NULL AND datediff_day("C"."DateFrom", "C"."DateTo") > 0 AND "C"."ClaimStatus" <> 1
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "Prod"."ProductCode", "Prod"."ProductName", (datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom"))), "I"."Gender", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwHospitalDays"
            AS
            SELECT sum(datediff_day("C"."DateFrom", "C"."DateTo")) AS hospitaldays,
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HFR"."RegionName" AS region,
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom")) AS "Age",
                "I"."Gender",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL AND "tblClaimItems"."RejectionReason" = 0
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL AND "tblClaimServices"."RejectionReason" = 0) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "HF"."ValidityTo" IS NULL AND "HFD"."ValidityTo" IS NULL AND datediff_day("C"."DateFrom", "C"."DateTo") > 0 AND "C"."ClaimStatus" <> 1
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "Prod"."ProductCode", "Prod"."ProductName", (datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom"))), "I"."Gender", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName", "HFD"."DistrictName", "HFR"."RegionName";


            CREATE OR REPLACE VIEW public."uvwAmountApproved"
            AS
            SELECT sum("Details"."Approved") AS "AmountApproved",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID",
                        sum("tblClaimItems"."PriceValuated") AS "Approved"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    GROUP BY "tblClaimItems"."ClaimID", "tblClaimItems"."ProdID"
                    UNION ALL
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID",
                        sum("tblClaimServices"."PriceValuated") AS "Approved"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL
                    GROUP BY "tblClaimServices"."ClaimID", "tblClaimServices"."ProdID") "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "C"."ClaimStatus" >= 8
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "Prod"."ProductCode", "Prod"."ProductName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwNumberFeedbackAnswerYes"
            AS
            SELECT count("F"."FeedbackID") AS "AnsYes",
                1 AS "QuestionId",
                month("F"."FeedbackDate") AS monthtime,
                quarter("F"."FeedbackDate") AS quartertime,
                year("F"."FeedbackDate") AS yeartime,
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName"
            FROM "tblFeedback" "F"
                JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
                JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "F"."ValidityTo" IS NULL AND "F"."CareRendered" = true
            GROUP BY (month("F"."FeedbackDate")), (quarter("F"."FeedbackDate")), (year("F"."FeedbackDate")), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "Prod"."ProductCode", "Prod"."ProductName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwNumberFeedbackResponded"
            AS
            SELECT count("F"."FeedbackID") AS "FeedbackResponded",
                month("F"."FeedbackDate") AS monthtime,
                quarter("F"."FeedbackDate") AS quartertime,
                year("F"."FeedbackDate") AS yeartime,
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblFeedback" "F"
                JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
                JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL) "Details" ON "F"."ClaimID" = "Details"."ClaimID"
                JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "F"."ValidityTo" IS NULL
            GROUP BY (year("F"."FeedbackDate")), (month("F"."FeedbackDate")), (quarter("F"."FeedbackDate")), "Prod"."ProductCode", "Prod"."ProductName", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";

            CREATE OR REPLACE VIEW public."uvwNumberFeedbackSent"
            AS
            SELECT count("F"."FeedbackPromptID") AS "FeedbackSent",
                month("F"."FeedbackPromptDate") AS monthtime,
                quarter("F"."FeedbackPromptDate") AS quartertime,
                year("F"."FeedbackPromptDate") AS yeartime,
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblFeedbackPrompt" "F"
                JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
                JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL) "Details" ON "F"."ClaimID" = "Details"."ClaimID"
                JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "F"."ValidityTo" IS NULL
            GROUP BY (year("F"."FeedbackPromptDate")), (month("F"."FeedbackPromptDate")), (quarter("F"."FeedbackPromptDate")), "Prod"."ProductCode", "Prod"."ProductName", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "HFD"."DistrictName", "HFR"."RegionName";

            
            CREATE OR REPLACE VIEW public."uvwOverallAssessment"
            AS
            SELECT "F"."Asessment",
                month("F"."FeedbackDate") AS monthtime,
                quarter("F"."FeedbackDate") AS quartertime,
                year("F"."FeedbackDate") AS yeartime,
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblFeedback" "F"
                JOIN "tblClaim" "C" ON "F"."ClaimID" = "C"."ClaimID"
                JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "F"."ValidityTo" IS NULL AND "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "HF"."ValidityTo" IS NULL AND "HFD"."ValidityTo" IS NULL;

            CREATE OR REPLACE VIEW public."uvwVisit"
            AS
            SELECT count("C"."ClaimID") AS "Visits",
                month("C"."DateFrom") AS monthtime,
                quarter("C"."DateFrom") AS quartertime,
                year("C"."DateFrom") AS yeartime,
                "HFR"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                datediff_year("I"."DOB", "C"."DateFrom") AS "Age",
                "I"."Gender",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion"
            FROM "tblClaim" "C"
                LEFT JOIN ( SELECT "tblClaimItems"."ClaimID",
                        "tblClaimItems"."ProdID"
                    FROM "tblClaimItems"
                    WHERE "tblClaimItems"."ValidityTo" IS NULL AND "tblClaimItems"."RejectionReason" = 0
                    UNION
                    SELECT "tblClaimServices"."ClaimID",
                        "tblClaimServices"."ProdID"
                    FROM "tblClaimServices"
                    WHERE "tblClaimServices"."ValidityTo" IS NULL AND "tblClaimServices"."RejectionReason" = 0) "Details" ON "C"."ClaimID" = "Details"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "Details"."ProdID" = "Prod"."ProdID"
                LEFT JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
                LEFT JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                LEFT JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
                LEFT JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                LEFT JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "HF"."ValidityTo" IS NULL AND "HFD"."ValidityTo" IS NULL AND datediff_day("C"."DateFrom", "C"."DateTo") = 0
            GROUP BY (month("C"."DateFrom")), (quarter("C"."DateFrom")), (year("C"."DateFrom")), "Prod"."ProductCode", "Prod"."ProductName", (datediff_year("I"."DOB", "C"."DateFrom")), "I"."Gender", "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName", "HFD"."DistrictName", "HFR"."RegionName";

            
            CREATE OR REPLACE VIEW public."uvwItemUtilization"
            AS
            SELECT sum("CI"."QtyProvided") AS "ItemUtilized",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "R"."RegionName" AS "Region",
                "DIns"."DistrictName",
                "Prod"."ProductCode",
                "Prod"."ProductName",
                datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom")) AS "Age",
                "I"."Gender",
                "Itm"."ItemType",
                "Itm"."ItemCode",
                "Itm"."ItemName",
                    CASE
                        WHEN datediff_day("C"."DateFrom", "C"."DateTo") > 0 THEN 'I'::bpchar
                        ELSE 'O'::bpchar
                    END AS "ItemCareType",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "ICD"."ICDCode",
                "ICD"."ICDName"
            FROM "tblClaimItems" "CI"
                JOIN "tblClaim" "C" ON "C"."ClaimID" = "CI"."ClaimID"
                LEFT JOIN "tblProduct" "Prod" ON "CI"."ProdID" = "Prod"."ProdID"
                JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
                JOIN "tblItems" "Itm" ON "CI"."ItemID" = "Itm"."ItemID"
                JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
                JOIN "tblDistricts" "DIns" ON "HF"."LocationId" = "DIns"."DistrictId"
                JOIN "tblRegions" "R" ON "DIns"."Region" = "R"."RegionId"
            WHERE "CI"."ValidityTo" IS NULL AND "C"."ValidityTo" IS NULL AND "Prod"."ValidityTo" IS NULL AND "Itm"."ValidityTo" IS NULL
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "R"."RegionName", "DIns"."DistrictName", "Prod"."ProductCode", "Prod"."ProductName", (datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom"))), "I"."Gender", "Itm"."ItemType", "Itm"."ItemCode", "Itm"."ItemName", (datediff_day("C"."DateFrom", "C"."DateTo")), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "ICD"."ICDCode", "ICD"."ICDName";

            CREATE OR REPLACE VIEW public."uvwServiceUtilization"
            AS
            SELECT sum("CS"."QtyProvided") AS "ServiceUtilized",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "R"."RegionName" AS "Region",
                "DIns"."DistrictName",
                "S"."ServType",
                "S"."ServCode",
                "S"."ServName",
                    CASE
                        WHEN datediff_day("C"."DateFrom", "C"."DateTo") > 0 THEN 'I'::bpchar
                        ELSE 'O'::bpchar
                    END AS "ServiceCareType"
            FROM "tblClaimServices" "CS"
                JOIN "tblClaim" "C" ON "CS"."ClaimID" = "C"."ClaimID"
                JOIN "tblServices" "S" ON "CS"."ServiceID" = "S"."ServiceID"
                JOIN "tblDistricts" "DIns" ON "C"."HFID" = "DIns"."DistrictId"
                JOIN "tblRegions" "R" ON "DIns"."Region" = "R"."RegionId"
            WHERE "CS"."ValidityTo" IS NULL AND "C"."ValidityTo" IS NULL AND "S"."ValidityTo" IS NULL
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "R"."RegionName", "DIns"."DistrictName", "S"."ServType", "S"."ServCode", "S"."ServName", (datediff_day("C"."DateFrom", "C"."DateTo"));

            
            CREATE OR REPLACE VIEW public."uvwItemExpenditures"
            AS
            SELECT sum("CI"."RemuneratedAmount") AS "ItemExpenditure",
                month(COALESCE("C"."DateTo", "C"."DateFrom")) AS monthtime,
                quarter(COALESCE("C"."DateTo", "C"."DateFrom")) AS quartertime,
                year(COALESCE("C"."DateTo", "C"."DateFrom")) AS yeartime,
                "R"."RegionName" AS "Region",
                "HFD"."DistrictName",
                "PR"."ProductCode",
                "PR"."ProductName",
                datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom")) AS "Age",
                "I"."Gender",
                "Itm"."ItemType",
                "Itm"."ItemCode",
                "Itm"."ItemName",
                    CASE
                        WHEN datediff_day("C"."DateFrom", "C"."DateTo") > 0 THEN 'I'::bpchar
                        ELSE 'O'::bpchar
                    END AS "ItemCareType",
                "HF"."HFLevel",
                "HF"."HFCode",
                "HF"."HFName",
                "C"."VisitType",
                "ICD"."ICDCode",
                "ICD"."ICDName",
                "DIns"."DistrictName" AS "IDistrictName",
                "W"."WardName",
                "V"."VillageName",
                "HFD"."DistrictName" AS "HFDistrict",
                "HFR"."RegionName" AS "HFRegion",
                "HFR"."RegionName" AS "ProdRegion"
            FROM "tblClaimItems" "CI"
                JOIN "tblClaim" "C" ON "CI"."ClaimID" = "C"."ClaimID"
                JOIN "tblProduct" "PR" ON "CI"."ProdID" = "PR"."ProdID"
                JOIN "tblInsuree" "I" ON "C"."InsureeID" = "I"."InsureeID"
                JOIN "tblFamilies" "F" ON "I"."FamilyID" = "F"."FamilyID"
                JOIN "tblVillages" "V" ON "V"."VillageId" = "F"."LocationId"
                JOIN "tblWards" "W" ON "W"."WardId" = "V"."WardId"
                JOIN "tblDistricts" "DIns" ON "DIns"."DistrictId" = "W"."DistrictId"
                JOIN "tblItems" "Itm" ON "CI"."ItemID" = "Itm"."ItemID"
                JOIN "tblHF" "HF" ON "C"."HFID" = "HF"."HfID"
                JOIN "tblICDCodes" "ICD" ON "C"."ICDID" = "ICD"."ICDID"
                JOIN "tblDistricts" "HFD" ON "HF"."LocationId" = "HFD"."DistrictId"
                JOIN "tblRegions" "R" ON "DIns"."Region" = "R"."RegionId"
                JOIN "tblRegions" "HFR" ON "HFR"."RegionId" = "HFD"."Region"
            WHERE "CI"."ValidityTo" IS NULL AND "C"."ValidityTo" IS NULL AND "PR"."ValidityTo" IS NULL AND "I"."ValidityTo" IS NULL AND "HF"."ValidityTo" IS NULL AND "HFD"."ValidityTo" IS NULL AND "C"."ClaimStatus" >= 8
            GROUP BY (month(COALESCE("C"."DateTo", "C"."DateFrom"))), (quarter(COALESCE("C"."DateTo", "C"."DateFrom"))), (year(COALESCE("C"."DateTo", "C"."DateFrom"))), "R"."RegionName", "PR"."ProductCode", "PR"."ProductName", (datediff_year("I"."DOB", COALESCE("C"."DateTo", "C"."DateFrom"))), "I"."Gender", "Itm"."ItemType", "Itm"."ItemCode", "Itm"."ItemName", (datediff_day("C"."DateFrom", "C"."DateTo")), "HF"."HFLevel", "HF"."HFCode", "HF"."HFName", "C"."VisitType", "ICD"."ICDCode", "ICD"."ICDName", "DIns"."DistrictName", "W"."WardName", "V"."VillageName", "HFD"."DistrictName", "HFR"."RegionName";


            
            """
        ),
    ]
