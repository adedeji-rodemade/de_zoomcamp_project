{{ 
    config(
        materialized='view'
    ) 
}}

WITH base_cte AS (
    SELECT
        wave,
        -- Use dbt_utils to generate unique id for each record
        {{ dbt_utils.generate_surrogate_key(['SiteID', 'Date']) }} || '-' || 
            CAST(ROW_NUMBER() OVER (PARTITION BY SiteID, Date) AS STRING) as id,
        {{ dbt.safe_cast("REGEXP_EXTRACT(wave, r'^(\d{4})')", 'INT64') }} AS year,

        -- Quarter extraction or fallback using mapped season
        CASE
            WHEN REGEXP_CONTAINS(wave, r'Q[1-4]') THEN REGEXP_EXTRACT(wave, r'(Q[1-4])')
            WHEN REGEXP_CONTAINS(LOWER(wave), r'autumn') THEN 'Q4'
            WHEN REGEXP_CONTAINS(LOWER(wave), r'spring') THEN 'Q2'
            WHEN REGEXP_CONTAINS(LOWER(wave), r'winter') THEN 'Q1'
            WHEN REGEXP_CONTAINS(LOWER(wave), r'summer') THEN 'Q3'
            ELSE NULL
        END AS quarter,

        -- Extract season or infer from quarter
        CASE
            WHEN REGEXP_CONTAINS(LOWER(wave), r'autumn') THEN 'autumn'
            WHEN REGEXP_CONTAINS(LOWER(wave), r'spring') THEN 'spring'
            WHEN REGEXP_CONTAINS(LOWER(wave), r'winter') THEN 'winter'
            WHEN REGEXP_CONTAINS(LOWER(wave), r'summer') THEN 'summer'
            WHEN REGEXP_CONTAINS(wave, r'Q1') THEN 'winter'
            WHEN REGEXP_CONTAINS(wave, r'Q2') THEN 'spring'
            WHEN REGEXP_CONTAINS(wave, r'Q3') THEN 'summer'
            WHEN REGEXP_CONTAINS(wave, r'Q4') THEN 'autumn'
            ELSE NULL
        END AS season,
        siteID,
        Date AS date_of_count,
        Weather,
        Day,
        CASE 
            WHEN Time BETWEEN TIME '05:00:00' AND TIME '07:59:59' THEN 'Early Morning'
            WHEN Time BETWEEN TIME '08:00:00' AND TIME '11:59:59' THEN 'Morning'
            WHEN Time BETWEEN TIME '12:00:00' AND TIME '16:59:59' THEN 'Afternoon'
            WHEN Time BETWEEN TIME '17:00:00' AND TIME '20:59:59' THEN 'Evening'
            ELSE 'Night'
        END AS time_of_day,
        Round,
        Direction,
        Mode,
        CAST(count AS numeric) AS active_count

    FROM {{source('staging','tfl_data')}}
),

final_cte AS (
    SELECT *,
        -- Compute program_start_date using quarter mapping
        PARSE_DATE('%Y-%m-%d', CONCAT(CAST(year AS STRING), '-', 
            CASE quarter
                WHEN 'Q1' THEN '01-01'
                WHEN 'Q2' THEN '04-01'
                WHEN 'Q3' THEN '07-01'
                WHEN 'Q4' THEN '10-01'
                ELSE '01-01'
            END
        )) AS season_start_date,

        -- Compute program_end_date by subtracting 1 day from next quarter
        DATE_SUB(PARSE_DATE('%Y-%m-%d', CONCAT(CAST(
            CASE WHEN quarter = 'Q4' THEN year + 1 ELSE year END AS STRING
        ), '-', 
            CASE quarter
                WHEN 'Q1' THEN '04-01'
                WHEN 'Q2' THEN '07-01'
                WHEN 'Q3' THEN '10-01'
                WHEN 'Q4' THEN '01-01'
                ELSE '01-01'
            END
        )), INTERVAL 1 DAY) AS season_end_date,
        CONCAT(year,"-",quarter) AS year_quarter

    FROM base_cte
)

SELECT * FROM final_cte
