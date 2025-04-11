{{
    config(
        materialized='table'
    )
}}

Select 
    Borough,
    SUM(active_count) as total_cycling
from {{ref("fct_cycling")}} 
group by Borough