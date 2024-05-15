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
let percentMap = {}
let loadingSimilarity = false
let fetcher = (selected) => {
    if (selected!=null && selected != undefined) { 
        loadingSimilarity = true;
        fetch(BASE_URL+"/music_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()]).then(x => x.json())
        .then(x => {
            percentMap = x; 
            Object.keys(percentMap).forEach(key => { colorMap[key] = colors[Math.round((size-1) * percentMap[key])] })
            loadingSimilarity=false;
        }).catch(err => console.log(err))
    }
}
$: fetcher(selected)
let top_ten;
let song_fetcher = (selected) => {
    fetch(BASE_URL+"/top_tracks?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()]).then(x => x.json())
        .then(x => {
            top_ten = x.slice(0,10)
        }).catch(err => console.log(err))
}
$: song_fetcher(selected) 
let recolor = (colors) => {
    Object.keys(percentMap).forEach(key => { colorMap[key] = colors[Math.round((size-1) * percentMap[key])] })
}
$: recolor(colors)


let view = "country-similarity"
let selectedSmallTitle = null;

</script>

<header>
    <div class="title-container">
        <h1 class="big-title">SoundSculptors</h1>
        <div class="small-titles">
            <span class="small-title {selectedSmallTitle === 'similarities' ? 'selected' : ''}" on:click={() => { selectedSmallTitle = 'similarities'; view = 'country-similarity'; }}>Music taste similarities</span>
            <span class="small-title {selectedSmallTitle === 'characteristics' ? 'selected' : ''}" on:click={() => {selectedSmallTitle = 'characteristics';view="radar"}}>Characteristics</span>
            <span class="small-title {selectedSmallTitle === 'genres' ? 'selected' : ''}" on:click={() => {selectedSmallTitle = 'genres'; view="genres"}}>Genres</span>
            <span class="small-title {selectedSmallTitle === 'related-artists' ? 'selected' : ''}" on:click={() => {selectedSmallTitle = 'related-artists';view="artists"}}>Related Artists</span>
        </div>
    </div>
</header>

<main>

<div class="header">
    <h3 class="header-item" on:click={() => view="country-similarity"} style={view=="country-similarity"?"text-decoration:underline":""}>Music Taste Similarities</h3> 
    <h3 class="header-item" on:click={() => view="radar"} style={view=="radar"?"text-decoration:underline":""}>Country Music Radar</h3>   
    <h3 class="header-item" on:click={() => view="listen-in"} style={view=="listen-in"?"text-decoration:underline":""}>Listen In</h3>  
</div>
<div class="container">
    <div class="map">
        {#if view == "country-similarity"}
            {#if loadingSimilarity}
                <div class="loading">
                    <RingLoader />
                </div>
            {/if}
            <Map bind:selected colors={colorMap} />
            <div class="similarity">
                Least similar music taste <div class="gradient" style="background: linear-gradient(90deg, {colors.join(', ')})" /> Most similar music taste
                <select bind:value={interpolator}>
                    {#each interpolators as option}
                    <option value={option[1]}>{option[0]}</option>
                    {/each}
                </select>
            </div>
        {:else if view == "radar"}
            <Map bind:selected /> 
        {:else if view == "genres"}
            <Map bind:selected /> 
        {:else if view == "listen-in"}
            <Map bind:selected  />
        {/if}

    </div>
    <div>
        {#if view == "country-similarity"}
            <h1>top 10 songs in {selected?.properties.name.toLowerCase() ?? "globally"}:</h1>
            {#if top_ten }
                <div>
                    {#each top_ten as song}
                       <div>{song["name"]} by {song["artist"]}</div>
                    {/each}
                </div>
            {/if}
        {:else if view == "radar"}
            <h2>Top songs average features in [selected country]</h2>
            <Radar bind:selected/>
        {:else if view == "genres"}
            <h2>Top genres in [selected country]</h2>
            <div class="genres_container">
                <p>The bar chart goes here</p>
            </div>

        {:else if view == "listen-in"}
            <h1>Listen in [selected country]</h1>
        {/if}
    </div>
</div>
{#if view == "artists"}
    <div class="input-container">
        <label class="input-label">Write the name of an artist:</label>
        <input type="text" placeholder="Enter artist name here">
    </div>

    <div class="graph_container">
        <p>The graph goes here</p>
        <!-- Add graph component here -->
</div>
{/if}
</main>

<style>
    .map {
        /* background-color: green; */
        /* width: wrap-content; */
        /* min-height: 40rem; */
        min-width: 60rem;
        /* max-width: 8000rem; */ 
    }
    .map_container {
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
    .graph_container {
    /* Style the container for the graph */
    margin-top: 20px;
    padding: 20px;
    border: 2px solid #ccc;
    border-radius: 5px;
    width: 50rem;
    height: 30rem;
  }

    .input-container {
    /* Use flexbox to align items horizontally */
    display: flex;
    align-items: center; /* Center items vertically */
    }

    .input-label {
    /* Style the label for the input */
    font-weight: bold;
    margin-right: 10px; /* Add margin to separate label from input */
    }

    .genres_container {
    /* Style the container for the genres */
    display: flex;
    flex-direction: column;
    align-items: center;
    }
</style>
