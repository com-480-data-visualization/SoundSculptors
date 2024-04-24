<script>
	// 	Note: Due to REPL limitations, full responsiveness may not work here. Download the example from here or from the website (https://layercake.graphics/example/Radar) and run locally to get all features.
	
	import { LayerCake, Svg } from 'layercake';
	import { scaleLinear } from 'd3-scale';

	import Radar from './_components/Radar.svelte';
	import AxisRadial from './_components/AxisRadial.svelte';

  // In your local project, you will more likely be loading this as a csv and converting it to json using @rollup/plugin-dsv
	import data from './_data//radarScores.js';

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
		xDomain={[0, 10]}
		xRange={({ height }) => [0, height / 2]}
		{data}
	>
		<Svg>
			<AxisRadial/>
			<Radar/>
		</Svg>
	</LayerCake>
</div>
