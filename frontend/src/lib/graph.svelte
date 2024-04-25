<script>
	// 	Note: Due to REPL limitations, full responsiveness may not work here. Download the example from here or from the website (https://layercake.graphics/example/Radar) and run locally to get all features.
	
	import { LayerCake, Svg } from 'layercake';
	import { scaleLinear } from 'd3-scale';

	import Radar from './_components/Radar.svelte';
	import AxisRadial from './_components/AxisRadial.svelte';
	const BASE_URL = "http://127.0.0.1:5000"
	import {markets, iso2CodesByCountryName} from '../lib/markets'

  // In your local project, you will more likely be loading this as a csv and converting it to json using @rollup/plugin-dsv
	// import data from './_data//radarScores.js';
	export let selected;
	let data = [{
		country: 'Allison',
		danceability: 5,
		speechiness: 1,
		energy: 6,
		acousticness: 8,
		instrumentalness: 0,
        liveness: 6,
	},];
	let fetcher = (selected) => {
		fetch(BASE_URL+"/music_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()]).then(x => x.json())
			.then(x => data = [x])
	} 
	$: fetcher(selected)
	$: console.log(data)
	const seriesKey = 'country';
	const xKey = ['danceability', 'speechiness', 'energy', 'acousticness', 'instrumentalness', 'liveness'];

	const seriesNames = Object.keys(data[0]).filter(d => d !== seriesKey);


	data.forEach(d => {
		seriesNames.forEach(name => {
			d[name] = +d[name];
		});
	});
</script>

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
		xDomain={[0, 15]}
		xRange={({ height }) => [0, height]}
		{data}
	>
		<Svg>
			<AxisRadial/>
			<Radar/>
		</Svg>
	</LayerCake>
</div>
