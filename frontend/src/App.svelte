<script>
import Map from './lib/map.svelte'
import {markets, iso2CodesByCountryName} from './lib/markets'
import { DoubleBounce } from 'svelte-loading-spinners';

const BASE_URL = "http://127.0.0.1:5000"
let selected;
let colors = {}
let loading = true
let setLoading = x => loading = true
$: fetch(BASE_URL+"/music_similarity?country_code="+
    iso2CodesByCountryName[selected?.properties.name.toLowerCase()])
    .then(x => x.json()).then(x => {colors = x; loading=false;})
    .catch(err => console.log(err))
$: setLoading(selected)
let view = "country-similarity"

</script>

<main>
{#if loading}
    <div class="loading">
        <DoubleBounce />
    </div>
{/if}
<div class="header">
    <h3 class="header-item" on:click={() => view="country-similarity"}>Music Taste Similarities</h3> 
    <h3 class="header-item" on:click={() => view="radar"}>Country Music Radar</h3>   
    <h3 class="header-item" on:click={() => view="listen-in"}>Listen In</h3>  
</div>
<div class="container">
    <div class="map">
        {#if view == "country-similarity"}
            <Map bind:selected {colors} />
        {:else if view == "radar"}
            <Map bind:selected />
        {:else if view == "listen-in"}
            <Map bind:selected  />
        {/if}

    </div>
    <div>
        {#if view == "country-similarity"}
            <h1>top 50 songs in {selected?.properties.name.toLowerCase() ?? "globally"}:</h1>
        {:else if view == "radar"}
            <h1> radar</h1>
        {:else if view == "listen-in"}
            <h1>listen in</h1>
        {/if}
    </div>
</div>
</main>

<style>
    .map {
        /* background-color: green; */
        /* width: wrap-content; */
        min-height: 30rem;
        min-width: 80rem;
    }
    .container {
        display:flex;
        /* background-color: green; */
    }
    .header {
        display: flex;
        justify-content: space-evenly;
    }
    .header-item:hover{
        color: grey;
    }
    .loading {
        position:fixed;
        top: 15rem;
        left: 25rem;
    }
</style>