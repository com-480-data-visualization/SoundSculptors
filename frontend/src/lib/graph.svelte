<script>
	// 	Note: Due to REPL limitations, full responsiveness may not work here. Download the example from here or from the website (https://layercake.graphics/example/Radar) and run locally to get all features.
	
	import { LayerCake, Svg } from 'layercake';
	import { scaleLinear } from 'd3-scale';
	import Radar from './_components/Radar.svelte';
	import AxisRadial from './_components/AxisRadial.svelte';
	const BASE_URL = "http://127.0.0.1:5000"
	import {markets, iso2CodesByCountryName} from '../lib/markets'

	// export let selected;
	// let data = [];
	let data = [{
		country: 'USA',
		danceability: .5,
		speechiness: .1,
		energy: .6,
		acousticness: .8,
		tempo: 0,
        duration_ms: .6,
	},];


	// let errorMessage = '';
	// let fetcher = (selected) => {
	// 	fetch(BASE_URL+"/radar_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()])
	// 		.then(x => {
	// 			if (!x.ok) {
	// 				throw new Error('Network response was not ok');
	// 			}
	// 			return x.json();
	// 		})
	// 		.then(x => {
	// 			console.log('Fetched data:', x);
	// 			x["tempo"] /= 140;
	// 			x["duration_ms"] /= 240000;
	// 			data = [x];
	// 		})
	// 		.catch(error => {
	// 			console.error('Fetch error:', error);
	// 			errorMessage = 'An error occurred while fetching the data. Please try again later.';
	// 		});
	// };
	// $: fetcher(selected)
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
	.chart-container {
    	min-width : 30rem;
		width: 60%;
		height: 60%;
	}
</style>

<div class="chart-container">
	<LayerCake
		padding={{ top: 60, right: 0, bottom: 7, left: 60 }}
		x={xKey}
		xDomain={[0, 2]}
		xRange={({ height }) => [0, height]}
		{data}
	>
		<Svg>
			<AxisRadial {data}/>
			<Radar {data}/>
		</Svg>
	</LayerCake>
</div>
