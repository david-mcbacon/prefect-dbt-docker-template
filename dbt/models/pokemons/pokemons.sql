{{
    config(
        materialized='table'
    )
}}

select
  cast(replace(replace(url, 'https://pokeapi.co/api/v2/pokemon/', ''),'/','') as INT64) as id
  , name
  , url
from 
  {{ source('pokemons', 'stg_pokemons') }}
