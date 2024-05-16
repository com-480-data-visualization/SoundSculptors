<script>
	// 	Note: Due to REPL limitations, full responsiveness may not work here. Download the example from here or from the website (https://layercake.graphics/example/Radar) and run locally to get all features.
	
	import { LayerCake, Svg } from 'layercake';
	import { scaleLinear } from 'd3-scale';
	import { RingLoader } from 'svelte-loading-spinners';

	import Radar from './_components/Radar.svelte';
	import AxisRadial from './_components/AxisRadial.svelte';
	export let BASE_URL
	import {markets, iso2CodesByCountryName} from '../lib/markets'

  // In your local project, you will more likely be loading this as a csv and converting it to json using @rollup/plugin-dsv
	// import data from './_data//radarScores.js';
	export let selected;
	let loading = false;
	let data = [{
		country: 'USA',
		danceability: .5,
		speechiness: .1,
		energy: .6,
		acousticness: .8,
		tempo: 0,
        duration_ms: .6,
	},];
	let fetcher = (selected) => {
		loading = true
		fetch(BASE_URL+"/radar_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()]).then(x => x.json())
			.then(x =>{
				x["tempo"] /= 140
				x["duration_ms"] /= 240000
				data = [x]
				console.log(data)
				loading = false;
			} )
	} 
	$: fetcher(selected)
	$: console.log(data)
	const seriesKey = 'country';
	const xKey = ['danceability', 'speechiness', 'energy', 'acousticness', 'tempo', 'duration_ms'];


	const seriesNames = Object.keys(data[0]).filter(d => d !== seriesKey);
	console.log(seriesNames); // Print the value of the 'seriesNames' variable



	data.forEach(d => {
		seriesNames.forEach(name => {
			d[name] = +d[name];
		});
	});
</script>

<!-- {#if errorMessage}
    <div class="error-message">{errorMessage}</div>
{/if} -->

<style>
	/*
		The wrapper div needs to have an explicit width and height in CSS.
		It can also be a flexbox child or CSS grid element.
		The point being it needs dimensions since the <LayerCake> element will
		expand to fill it.
	*/
	.loading {
        position:relative;
        top: 15rem;
        left: 20rem;
    }
	.chart-container {
    	min-width : 30rem;
		width: 60%;
		height: 60%;
	}
</style>

<div class="chart-container">
	
	{#if !selected}
		<p>Click on a country to see its music radar!</p>
	{:else}
		{#if loading}
                <div class="loading">
                    <RingLoader />
                </div>
   		{:else}
			{#if 'error' in data[0]}
				<p>Spotify servers are experiencing high load at this time, please try again later.</p>
			{:else}
				
				<LayerCake
					padding={{ top: 60, right: 0, bottom: 7, left: 60 }}
					x={xKey}
					xDomain={[0, 2]}
					xRange={({ height }) => [0, height]}
					{data}
				>
					<Svg>
						<AxisRadial />
						<Radar />
					</Svg>
				</LayerCake>
			{/if}
		{/if}
	{/if}
</div>
