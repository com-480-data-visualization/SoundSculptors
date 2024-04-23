<script>
import Map from './lib/map.svelte'
let selected;
$: console.log(selected?.properties.name ?? '')
</script>

<main>
<Map bind:selected />
</main>

<style>

</style>