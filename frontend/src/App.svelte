<script>
import Radar from './lib/graph.svelte'
import Map from './lib/map.svelte'
import {markets, iso2CodesByCountryName} from './lib/markets'
import { RingLoader } from 'svelte-loading-spinners';
import * as d3chromatic from 'd3-scale-chromatic';
import { color } from 'd3';

const BASE_URL = "http://127.0.0.1:5000"

$: interpolators = (Object.entries(d3chromatic).filter(([key, value]) => key.startsWith('interpolate')))
$: step = 1 / size;
let size = 100;
let interpolator = d3chromatic.interpolateSpectral
$: colors = Array.from({ length: size }, (_, i) => interpolator(i * step));
$: console.log(colorMap)



let selected;
let colorMap = {}
let loading = false
let fetcher = (selected) => {
    if (selected!=null && selected != undefined) { 
        console.log("FETCHING")
        loading = true;
        fetch(BASE_URL+"/music_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()]).then(x => x.json())
        .then(x => {
            console.log("LOADED")
            colorMap = x; 
            Object.keys(colorMap).forEach(key => { colorMap[key] = colors[Math.round((size-1) * colorMap[key])] })
            loading=false;
        }).catch(err => console.log(err))
    }
}
$: fetcher(selected)



let view = "country-similarity"



</script>

<main>
{#if loading}
    <div class="loading">
        <RingLoader />
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
            <Map bind:selected colors={colorMap} />
            <div class="similarity">
                Least similar music <div class="gradient" style="background: linear-gradient(90deg, {colors.join(', ')})" /> Most Similar
                <select bind:value={interpolator}>
                    {#each interpolators as option}
                    <option value={option[1]}>{option[0]}</option>
                    {/each}
                </select>
            </div>
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
            <!-- <h1>radar</h1> -->
            <Radar />
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
        /* min-height: 40rem; */
        min-width: 60rem;
        /* max-width: 8000rem; */ 
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
    .gradient {
		height: 1rem;
        width: 20rem;
	}

    .similarity{
        display: flex;
        justify-content: space-evenly;
    }
</style>
