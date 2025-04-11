{{
    config(
        materialized='table'
    )
}}

Select 
    s.SiteID,
    s.year as wave_year,
    s.quarter as wave_quarter,
    s.year_quarter as wave_year_quarter,
    s.season,
    s.season_start_date,
    s.season_end_date,
    s.Weather,
    s.Day as day_type,
    s.time_of_day,
    s.Direction,
    s.Mode,
    d.Borough,
    d.Functional_area,
    CASE 
        WHEN d.Road_type = "0" THEN "00 Unclassified Road"
        ELSE d.Road_type
    END road_type,
    s.active_count,
from {{ref("stg_cycling_data")}} s
inner join {{ref("dim_location_lookup")}} d 
    on s.siteID=d.site_ID