<script>
import Radar from './lib/graph.svelte'
import Map from './lib/map.svelte'
import { onMount } from "svelte";
import {markets, iso2CodesByCountryName} from './lib/markets'
import { RingLoader } from 'svelte-loading-spinners';
import * as d3chromatic from 'd3-scale-chromatic';
import { color } from 'd3';
import * as d3 from "d3";

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


// Genres
let loadingGenre = false
let genres = [];
let genre_fetcher = (selected) => {
    if (selected!=null && selected != undefined) { 
        loadingGenre = true;
        fetch(BASE_URL+"/top_genres?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()])
                .then(x => x.json())
                .then(data => {
                    genres = Object.entries(data); // Assuming data is a dict of genre name and percentage
                    loadingGenre = false;
                })
                .catch(err => {
                    console.log(err);
                    loadingGenre = false;
                });
    }
}

// Related Artists
let artistName = "";
let artistDetails = null;
let graphData = { nodes: [], links: [] };

const fetchArtistDetails = async (artistName) => {
    try {
        const response = await fetch(BASE_URL+`/artist_details?artist_name=${artistName}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching artist details:", error);
    }
};

const updateGraph = (data) => {
    graphData.nodes = [{ id: artistName, group: 1 }];
    graphData.links = [];

    data.related_artists.forEach((relatedArtist, index) => {
        graphData.nodes.push({ id: relatedArtist, group: 2 });
        graphData.links.push({ source: artistName, target: relatedArtist });
    });

    renderGraph();
};

const renderGraph = () => {
    const width = 800;
    const height = 600;

    d3.select("#graph").select("svg").remove();

    const svg = d3.select("#graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.links).id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
        .selectAll("line")
        .data(graphData.links)
        .enter()
        .append("line")
        .attr("stroke-width", 1.5)
        .attr("stroke", "#999");

    const node = svg.append("g")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter()
        .append("circle")
        .attr("r", 10)
        .attr("fill", d => d.group === 1 ? "blue" : "green")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("click", (event, d) => {
            fetchArtistDetails(d.id).then(details => {
                artistDetails = details;
            });
        });

    const text = svg.append("g")
        .selectAll("text")
        .data(graphData.nodes)
        .enter()
        .append("text")
        .attr("dy", -10)
        .attr("dx", 12)
        .text(d => d.id);

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        text
            .attr("x", d => d.x)
            .attr("y", d => d.y);
    });

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
};

const handleSubmit = () => {
    fetchArtistDetails(artistName).then(details => {
        updateGraph(details);
        artistDetails = details;
    });
};




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

<!-- <div class="header">
    <h3 class="header-item" on:click={() => view="country-similarity"} style={view=="country-similarity"?"text-decoration:underline":""}>Music Taste Similarities</h3> 
    <h3 class="header-item" on:click={() => view="radar"} style={view=="radar"?"text-decoration:underline":""}>Country Music Radar</h3>   
    <h3 class="header-item" on:click={() => view="listen-in"} style={view=="listen-in"?"text-decoration:underline":""}>Listen In</h3>  
</div> -->
<div class="map_container">
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
            {#if loadingGenre}
                <div class="loading">
                    <RingLoader />
                </div>
            {/if}
            <Map bind:selected /> 
        {:else if view == "listen-in"}
            <Map bind:selected  />
        {/if}

    </div>
    <div>
        {#if view == "country-similarity"}
            <h1>Top 10 songs in {selected?.properties.name ?? "Globally"}:</h1>
            {#if top_ten }
                <div>
                    {#each top_ten as song}
                       <div>{song["name"]} by {song["artist"]}</div>
                    {/each}
                </div>
            {/if}
        {:else if view == "radar"}
            <h2>Top songs average features in {selected?.properties.name ?? "??"}</h2>
            <Radar bind:selected/>
        {:else if view == "genres"}
            <h2>Top genres in {selected?.properties.name}</h2>
            <div class="genres_container">
                {#if genres.length > 0}
                    {#each genres as [genre, percentage]}
                        <div class="bar">
                            <span>{genre}</span>
                            <div style="width: {percentage}%;"></div>
                            <span>{percentage}%</span>
                        </div>
                    {/each}
                {:else}
                    <p>No data available.</p>
                {/if}
            </div>

        {:else if view == "listen-in"}
            <h1>Listen in [selected country]</h1>
        {/if}
    </div>
</div>
{#if view == "artists"}
    <div class="input-container">
        <label class="input-label">Write the name of an artist:</label>
        <input type="text" bind:value={artistName} placeholder="Enter artist name here">
        <button on:click={handleSubmit}>Search</button>
    </div>

    <div class="graph_container">
        <div id="graph"></div>
        {#if artistDetails}
            <div class="details_container">
                <img src={artistDetails.image_url} alt="Artist Picture" width="150">
                <p>Artist name: {artistName}</p>
                <p>Number of followers: {artistDetails.follower_number}</p>
                <p>Popularity: {artistDetails.popularity}</p>
                <p>Number of albums: {artistDetails.album_number}</p>
            </div>
        {/if}
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

    .bar {
        display: flex;
        align-items: center;
    }
    .bar div {
        background-color: lightgray;
        height: 20px;
        margin-left: 10px;
    }
    .details_container {
        margin-left: 20px;
    }
</style>
