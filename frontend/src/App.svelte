<script>
import Radar from './lib/graph.svelte'
import {markets, iso2CodesByCountryName} from './lib/markets'

//let selected;
//let colors = {}
//$: fetch("http://127.0.0.1:5000/music_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()]).then(x => x.json()).then(x => colors = x).catch(err => console.log(err))
//$: console.log(colors)
</script>

<main>
<div>
<div class="map">
<Radar/>
</div>
<div class="chart-container">
    <Radar/>

</div>
</div>
</main>

<style>
    .map {
        /* background-color: green; */
        /* width: wrap-content; */
    }
</style>