<script>
import Radar from './lib/graph.svelte'
import Map from './lib/map.svelte'
import { onMount } from "svelte";
import {markets, iso2CodesByCountryName} from './lib/markets'
import { RingLoader } from 'svelte-loading-spinners';
import * as d3chromatic from 'd3-scale-chromatic';
import { color } from 'd3';
import * as d3 from "d3";

// const BASE_URL = "https://ktotam.pythonanywhere.com"
const BASE_URL = "http://localhost:5001"

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
$: genre_fetcher(selected) 
let loadingGenre = false
let genres = [];
let errorMessage = "";
let genre_fetcher = (selected) => {
    if (selected != null && selected != undefined) {
        loadingGenre = true;
        errorMessage = ""; // Reset the error message
        fetch(BASE_URL + "/top_genres?country_code=" + iso2CodesByCountryName[selected?.properties.name.toLowerCase()])
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error fetching top genres");
                }
                return response.json();
            })
            .then(data => {
                genres = Object.entries(data); // Assuming data is a dict of genre name and percentage
                loadingGenre = false;
            })
            .catch(err => {
                console.log(err);
                loadingGenre = false;
                errorMessage = "Sorry! No data available for this country. Choose another one!";
            });
    }
};

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
        .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100)) // Increase distance for longer edges
        .force("charge", d3.forceManyBody().strength(-300)) // Increase strength for more spread out nodes
        .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graphData.links)
        .enter()
        .append("line")
        .attr("stroke-width", 2)
        .attr("stroke", "#999");

    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter()
        .append("circle")
        .attr("r", 10)
        .attr("fill", d => d.group === 1 ? "#e8f5e9" : "green")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("click", (event, d) => {
            handleSubmit(d.id); // Call handleSubmit with the clicked artist's name
        });
        

    const text = svg.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(graphData.nodes)
        .enter()
        .append("text")
        .attr("dy", -10)
        .attr("dx", 12)
        .attr("font-size", d => d.id === artistName ? "18px" : "12px") // Larger font for central node
        .attr("font-family", "Arial, sans-serif") 
        .attr("font-weight", d => d.id === artistName ? "bold" : "normal") // Bold font for central node
        .text(d => d.id === artistName ? d.id.toUpperCase() : d.id) // Capitalize central artist name

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
            .attr("y", d => d.y)
            .attr("dx", d => {
                if (d.id === artistName) return 0; // Center text for central node
                else if (d.x > width / 2) return 12; // Right side
                else if (d.x < width / 2) return -12; // Left side
                else return 0; // Center
            })
            .attr("dy", d => {
                if (d.id === artistName) return 4; // Slight offset for readability
                else if (d.y > height / 2) return 12; // Bottom side
                else if (d.y < height / 2) return -12; // Top side
                else return 0; // Center
            })
            .attr("text-anchor", d => {
                if (d.id === artistName) return "middle"; // Center text for central node
                else if (d.x > width / 2) return "start"; // Right side
                else if (d.x < width / 2) return "end"; // Left side
                else return "middle"; // Center
            });
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

const handleSubmit = (name) => {
    artistName = name; // Update the global artistName variable
    fetchArtistDetails(name).then(details => {
        updateGraph(details);
        artistDetails = details;
    });
};

// handle the search button click
const handleSearchClick = () => {
    handleSubmit(artistName);
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
        <div class="next_to_map_container">
            <h2>Top 10 songs in {selected?.properties.name ?? "the world"}:</h2>
            {#if top_ten }
                <div class="song-list">
                    {#each top_ten as song, index}
                        <div>{index + 1}. <span class="song-name">{song["name"]}</span> by {song["artist"]}</div>
                    {/each}
                </div>
            {/if}
        </div>
        {:else if view == "radar"}
        <div class="next_to_map_container">
            {#if selected!=null}
                <h2><center>Top songs average features in {selected?.properties.name}</center></h2>
                <Radar {BASE_URL} bind:selected/>
            {:else}
                <p><center>Select a country to see the top songs average features!</center></p>
            {/if}
        </div>
        {:else if view == "genres"}
            <div class="next_to_map_container">
                {#if selected!=null}
                    <h2>Top genres in {selected?.properties.name}</h2>
                    {#if errorMessage!=""}
                        <p><center>{errorMessage}</center></p>
                    {:else if genres.length > 0}
                        {#each genres as [genre, percentage]}
                            <div class="bar">
                                <span class="genre">{genre.charAt(0).toUpperCase()+ genre.slice(1).toLowerCase()}</span>
                                <div class="bar-inner" style="width: {percentage}%;"></div>
                                <span class="percentage">{percentage}%</span>
                            </div>
                        {/each}
                    {:else}
                        <p><center>Sorry! No data available for this country. Choose another one!</center></p>
                    {/if}
                {:else}
                    <p><center>Select a country to see the top genres!</center></p>
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
    <input type="text" bind:value={artistName} placeholder="Enter artist name here" on:keydown={(event) => event.key === 'Enter' && handleSubmit(artistName)}>
    <button on:click={handleSearchClick}>Search</button>
</div>

<div class="main_container">
    <div class="graph_container">
        <div id="graph"></div>
    </div>
    {#if artistDetails}
        <div class="details_container">
            <img src={artistDetails.image_url} alt="Artist Picture" width="180">
            <p><strong>Artist name: {artistName.toUpperCase()}</strong></p>
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
    .input-container {
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .main_container {
        display: flex;
        align-items: center;
    }

    .graph_container {
        flex: 3;
        display: flex;
        padding: 20px;
        border: 2px solid #ccc;
        border-radius: 5px;
        width: 50rem;
        height: 30rem;
        align-items: center;
        justify-content: center;
    }

    .details_container {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        border: 2px solid #ccc;
        border-radius: 5px;
        height: 30rem;
    }

    .input-label {
        margin-right: 10px;
    }

    input[type="text"] {
        padding: 5px;
        margin-right: 10px;
    }

    button {
        padding: 5px 10px;
    }

    .input-label {
    /* Style the label for the input */
    font-weight: bold;
    margin-right: 10px; /* Add margin to separate label from input */
    }

    .next_to_map_container {
    /* Style the container for the genres */
    display: flex;
    flex: 1;  
    flex-direction: column;
    align-items: center;
    gap: 10px;
    border: 5px solid #ccc;
    border-radius: 10px;
    height: 30rem;
    width: 28rem;
    }

    .bar {
        display: flex;
        align-items: center;
        width: 100%;
    }
    
    .genre {
        width: 200px; /* Fixed width to align all bar labels */
        text-align: left;
        margin-right: 10px;
        margin-left: 10px;
    }

    .bar-inner {
        background-color: green;
        height: 20px; /* Adjust height as needed */
        margin-right: 10px;
    }

    .percentage {
        white-space: nowrap;
    }
    .song-list {
    line-height: 1.8; /* Adjust this value as needed */
    margin-left: 10px;
    }
    .song-name {
        color: green;
        font-weight: bold;
    }


</style>
