{{
    config(
        materialized='table'
    )
}}

Select 
    wave_year,
    SUM(active_count) as total_cycling
from {{ref("fct_cycling")}} 
group by wave_year