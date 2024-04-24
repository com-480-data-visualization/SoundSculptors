<script>
import Map from './lib/map.svelte'
import {markets, iso2CodesByCountryName} from './lib/markets'

let selected;
let colors = {}
$: fetch("http://127.0.0.1:5000/music_similarity?country_code="+iso2CodesByCountryName[selected?.properties.name.toLowerCase()]).then(x => x.json()).then(x => colors = x).catch(err => console.log(err))
$: console.log(colors)

let view = "country-similarity"

</script>

<main>
<div class="container">
<div class="map">
<Map bind:selected {colors} />
</div>
<div>
    <h1> radar</h1>
</div>
</div>
</main>

<style>
    .map {
        /* background-color: green; */
        /* width: wrap-content; */
        min-height: 30rem;
        min-width: 80rem;
    }
    .container {
        display:flex;
        /* background-color: green; */
    }
</style>