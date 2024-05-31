<script>
	
	import { LayerCake, Svg } from 'layercake';
	import { scaleLinear } from 'd3-scale';
	import { RingLoader } from 'svelte-loading-spinners';
	import Radar from './_components/Radar.svelte';
	import AxisRadial from './_components/AxisRadial.svelte';
	export let BASE_URL
	import {markets, iso2CodesByCountryName} from '../lib/markets'


	export let selected;
	let loading = false;
	let data = [{}];
	const TEMPO_MAX = 200;
	const DURATION_MS_MAX = 480000; // 8 minutes
	let errorMessage = "";
	let fetcher = (selected) => {
		loading = true
		fetch(BASE_URL+"/radar_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()])
			.then(response => {
                if (!response.ok) {
                    throw new Error("Error fetching features!");
                }
                return response.json();
            })
			.then(x =>{
				x["tempo"] /= TEMPO_MAX
				x["duration_ms"] /= DURATION_MS_MAX
				data = [x]
				console.log(data)
				loading = false;
			} )
            .catch(err => {
                console.log(err);
                loading = false;
                errorMessage = "Sorry! No data available for this country. Choose another one!";
            });
	} 
	$: fetcher(selected)
	const seriesKey = 'country';
	const xKey = ['danceability', 'speechiness', 'energy', 'acousticness', 'tempo', 'duration_ms'];
	const seriesNames = Object.keys(data[0]).filter(d => d !== seriesKey);


	data.forEach(d => {
		seriesNames.forEach(name => {
			d[name] = +d[name];
		});
	});
</script>


<style>
	.loading {
        position:relative;
        top: 0.5rem;
        left: 0rem;
    }
	.chart-container {
		display: flex;	
		justify-content: center;
		align-items: center;
    	min-width : 30rem;
		width: 70%;
		height: 70%;
		/* flex-grow: 1; */
	}
</style>

<div class="chart-container">
	
	{#if !selected}
	<span class="error-message">Click on a country to see its music radar!</span>
	{:else}
		{#if loading}
			<div class="loading">
				<RingLoader />
			</div>
   		{:else}
			{#if errorMessage}
				<span class="error-message">{errorMessage}</span>
			{:else if data.length === 0	}
				<span class="error-message">No data available for this country. Please choose another one!</span>
			{:else}
				<LayerCake
					padding={{ top: 40, right: 10, bottom: 7, left: 10 }}
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
